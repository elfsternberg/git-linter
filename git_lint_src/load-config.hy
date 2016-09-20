#!/usr/bin/env hy
(import ConfigParser os subprocess operator re gettext sys getopt)
(def _ gettext.gettext)
(def *version* "0.0.2")

(defn tap [a] (print "TAP:" a) a)

(def optlist [["o" "only" true (_ "A comma-separated list of only those linters to run") ["x"]]
              ["x" "exclude" true (_ "A comma-separated list of linters to skip") []]
              ["l" "linters" false (_ "Show the list of configured linters")]
              ["b" "base" false (_ "Check all changed files in the repository, not just those in the current directory.") []]
              ["a" "all" false (_ "Scan all files in the repository, not just those that have changed.")]
              ["e" "every" false (_ "Short for -b -a, scan everything")]
              ["w" "workspace" false (_ "Scan the workspace") ["s"]]
              ["s" "staging" false (_ "Scan the staging area (pre-commit).") []]
              ["g" "changes" false (_ "Report lint failures only for diff'd sections") ["l"]]
              ["m" "complete" false (_ "Report lint failures for all files") []]
              ["c" "config" true (_ "Path to config file") []]
              ["h" "help" false (_ "This help message") []]
              ["v" "version" false (_"Version information") []]])

; Given a set of command-line arguments, compare that to a mapped
; version of the optlist and return a canonicalized dictionary of all
; the arguments that have been set.  For example "-c" and "--config"
; will both be mapped to "config".

; Given a prefix of one or two dashes and a position in the above
; array, creates a function to map either the short or long option
; to the option name.

(defn make-opt-assoc [prefix pos]
  (fn [acc it] (assoc acc (+ prefix (get it pos)) (get it 1)) acc)) 

; Using the above, create a full map of all arguments, then return a
; function ready to look up any argument and return the option name.  

(defn make-options-rationalizer [optlist]
  (let [
        [short-opt-assoc (make-opt-assoc "-" 0)]
        [long-opt-assoc (make-opt-assoc "--" 1)]
        [fullset 
         (reduce (fn [acc i] (-> (short-opt-assoc acc i)
                                 (long-opt-assoc i))) optlist {})]]
    (fn [acc it] (do (assoc acc (get fullset (get it 0)) (get it 1)) acc))))

(defn print-version []
  (print (.format "git-lint (hy version {})" *version*))
  (print "Copyright (c) 2008, 2016 Kenneth M. \"Elf\" Sternberg <elf.sternberg@gmail.com>")
  (sys.exit))

(defn print-help []
  (print "Usage: git lint [options] [filename]")
  (for [item optlist] (print (.format " -{:<1}  --{:<12}  {}" (get item 0) (get item 1) (get item 3))))
  (sys.exit))

(defn get-git-response [cmd]
  (let [[fullcmd (+ ["git"] cmd)]
        [process (subprocess.Popen fullcmd
                                   :stdout subprocess.PIPE
                                   :stderr subprocess.PIPE)]
        [(, out err) (.communicate process)]]
    (, out err process.returncode)))

(defn run-git-command [cmd]
  (let [[fullcmd (+ ["git"] cmd)]]
    (subprocess.call fullcmd
                     :stdout subprocess.PIPE
                     :stderr subprocess.PIPE)))

(defn get-shell-response [fullcmd]
  (let [[process (subprocess.Popen fullcmd
                                   :stdout subprocess.PIPE
                                   :stderr subprocess.PIPE
                                   :shell True)]
        [(, out err) (.communicate process)]]
    (, out err process.returncode)))

(def git-base (let [[(, out error returncode)
                     (get-git-response ["rev-parse" "--show-toplevel"])]]
                (if (not (= returncode 0)) None (.rstrip out))))

(defn find-config-file [options]
  (if (.has_key options "config")
    (let [[config (get options "config")]
          [configpath (os.path.abspath config)]]
      (if (os.path.isfile configpath)
        configpath
        (sys.exit (.format (_ "Configuration file not found: {}\n") config))))
    (let [[home (os.path.join (.get os.environ "HOME"))]
          [possibles (, (os.path.join git-base ".git-lint")
                        (os.path.join git-base ".git-lint/config")
                        (os.path.join home ".git-lint")
                        (os.path.join home ".git-lint/config"))]
          [matches (list (filter os.path.isfile possibles))]]
      (if (len matches) (get matches 0) (sys.exit (_ "No configuration file found"))))))

(defn load-config-file [path]
  (let [[configloader (.SafeConfigParser ConfigParser)]
        [config {}]]
    (.read configloader path)
    (.set configloader "DEFAULT" "repdir" git-base)
    (for [section (.sections configloader)]
      (let [[pairs {}]]
        (for [(, k v) (.items configloader section)]
          (assoc pairs k v))
        (assoc config section pairs)))
    config))

(defn make-match-filter-matcher [extensions]
  (->> (map (fn [s] (.split s ",")) extensions)
       (reduce operator.add)
       (map (fn [s] (.strip s)))
       (set)
       (filter (fn [s] (not (= 0 (len s)))))
       (map (fn [s] (.sub re "^\." "" s)))
       (.join "|")
       ((fn [s] (+ "\.(" s ")$")))
       ((fn [s] (re.compile s re.I)))))

(defn make-match-filter [config]
  (let [[matcher (make-match-filter-matcher (map (fn [v] (.get v "match" "" ))
                                                    (.itervalues config)))]]
    (print matcher)
    (fn [path] (.search matcher path))))

(defn print-linters [config]
  (print (_ "Currently supported linters:"))
  (for [(, linter items) (.iteritems config)]
    (print (.format "{:<14} {}" linter (.get items "comment" "")))))

(defn git-lint-main [options]
  (print git-base)
  (print (os.path.abspath __file__))
  (let [[config (load-config-file (find-config-file))]]
    (print options)
    (print config)
    (print (make-match-filter config))))

(defmain [&rest args]
  (try
   (let [[optstringsshort 
          (.join "" (map (fn [i] (+ (. i [0]) (cond [(. i [2]) ":"] [true ""]))) optlist))]
         [optstringslong 
          (list (map (fn [i] (+ (. i [1]) (cond [(. i [2]) "="] [true ""]))) optlist))]
         [(, opt arg) 
          (getopt.getopt (slice args 1) optstringsshort optstringslong)]
         [rationalize-options 
          (make-options-rationalizer optlist)]
         [options (reduce (fn [acc i] (rationalize-options acc i)) opt {})]
         [config (load-config-file (find-config-file options))]]
     (cond [(.has_key options "help") (print-help)]
           [(.has_key options "version") (print-version)]
           [(.has_key options "linters") (print-linters config)]
           [true (git-lint-main options)]))
   (catch [err getopt.GetoptError]
       (print (str err))
     (print-help))))

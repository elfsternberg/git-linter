#!/usr/bin/env hy
(import os re subprocess sys gettext)
(def *version* "0.0.2")
(def _ gettext.gettext)

; 0: Short opt, 1: long opt, 2: takes argument, 3: help text
(def optlist [["o" "only" true (_ "A comma-separated list of only those linters to run") ["x"]]
              ["x" "exclude" true (_ "A comma-separated list of linters to skip") []]
              ["b" "base" false (_ "Check all changed files in the repository, not just those in the current directory.") []]
              ["a" "all" false (_ "Scan all files in the repository, not just those that have changed.")]
              ["w" "workspace" false (_ "Scan the workspace") ["s"]]
              ["s" "staging" false (_ "Scan the staging area (pre-commit).") []]
              ["g" "changes" false (_ "Report lint failures only for diff'd sections") ["l"]]
              ["l" "complete" false (_ "Report lint failures for all files") []]
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
         (ap-reduce (-> (short-opt-assoc acc it)
                        (long-opt-assoc it)) optlist {})]]
    (fn [acc it] (do (assoc acc (get fullset (get it 0)) (get it 1)) acc))))

  
  

(defn print-version []
  (print (.format "git-lint (hy version {})" *version*))
  (print "Copyright (c) 2008, 2014 Kenneth M. \"Elf\" Sternberg <elf.sternberg@gmail.com>")
  (sys.exit))

(defn print-help []
  (print "Usage: git lint [options] [filename]")
  (ap-each optlist (print (.format "	-{}	--{}	{}" (get it 0) (get it 1) (get it 3))))
  (sys.exit))

; `lint` should be a directory under your .git where you store the RCs
; for your various linters.  If you want to use a global one, you'll
; have to edit the configuration entries below.

(def *config-path*
  

  (os.path.join (.get os.environ "GIT_DIR" "./.git") "lint"))

(def *git-modified-pattern* (.compile re "^[MA]\s+(?P<name>.*)$"))

(def *checks*
  [
;   {
;    "output" "Checking for debugger commands in Javascript..."
;    "command" "grep -n debugger {filename}"
;    "match_files" [".*\.js$"]
;    "print_filename" True
;    "error_condition" "output"
;    }
   {
    "output" "Running Jshint..."
    "command" "jshint -c {config_path}/jshint.rc {filename}"
    "match_files" [".*\.js$"]
    "print_filename" False
    "error_condition" "error"
    }
   {
    "output" "Running Coffeelint..."
    "command" "coffeelint {filename}"
    "match_files" [".*\.coffee$"]
    "print_filename" False
    "error_condition" "error"
    }
   {
    "output" "Running JSCS..."
    "command" "jscs -c {config_path}/jscs.rc {filename}"
    "match_files" [".*\.js$"]
    "print_filename" False
    "error_condition" "error"
    }
   {
    "output" "Running pep8..."
    "command" "pep8 -r --ignore=E501,W293,W391 {filename}"
    "match_files" [".*\.py$"]
    "print_filename" False
    "error_condition" "error"
    }
   {
    "output" "Running xmllint..."
    "command" "xmllint {filename}"
    "match_files" [".*\.xml"]
    "print_filename" False
    "error_condition" "error"
    }
   ]
  )

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

(defn derive-max-code [code-pairs]
  (reduce
   (fn [m i] (if (> (abs (get i 0)) (abs m)) (get i 0) m))
   code-pairs 0))

(defn derive-message-bodies [code-pairs]
  (lmap (fn [i] (get i 1)) code-pairs))

(defn lmap (pred iter) (list (map pred iter)))

(defn encode-shell-messages [prefix messages]
  (lmap (fn [line] (.format "{}{}" prefix (.decode line "utf-8")))
        (.splitlines messages)))

(defn run-external-checker [filename check]
  (let [[cmd (-> (get check "command")
                 (.format
                  :filename filename
                  :config_path *config-path*))]
        [(, out err returncode) (get-shell-response cmd)]]
    (if (or (and out (= (.get check "error_condition" "error") "output"))
            err
            (not (= returncode 0)))
      (let [[prefix (if (get check "print_filename")
                      (.format "\t{}:" filename)
                      "\t")]
            [output (+ (encode-shell-messages prefix out)
                       (if err (encode-shell-messages prefix err) []))]]
        [(or returncode 1) output])
      [0 []])))

(defn matches-file [filename match-files]
  (any (map (fn [match-file] (-> (.compile re match-file)
                                 (.match filename)))
            match-files)))

(defn check-scan-wanted [filename check]
  (cond [(and (in "match_files" check)
              (not (matches-file filename (get check "match_files")))) false]
        [(and (in "ignore_files" check)
              (matches-file filename (get check "ignore_files"))) false]
        [true true]))

(defn check-files [filenames check]
  (let [[filenames-to-check
         (filter (fn [filename] (check-scan-wanted filename check)) filenames)]
        [results-of-checks
         (lmap (fn [filename]
                 (run-external-checker filename check)) filenames-to-check)]
        [messages (+ [(get check "output")] 
                     (derive-message-bodies results-of-checks))]]
    [(derive-max-code results-of-checks) messages]))

(defn gather-all-filenames []
  (let [[build-filenames
         (fn [filenames]
           (map
            (fn [f] (os.path.join (get filenames 0) f)) (get filenames 2)))]]
    (list
     (flatten
      (list-comp (build-filenames o) [o (.walk os ".")])))))

(defn gather-staged-filenames [against]
  (let [[(, out err returncode)
         (get-git-response ["diff-index" "--name-status" against])]
        [lines (.splitlines out)]
        [matcher 
         (fn [line] 
           (.match *git-modified-pattern* (.decode line "utf-8")))]]
    (list
     (filter
      (fn [x] (not (= x "")))
      (list-comp (.group match "name") [match (map matcher lines)] match)))))

(defn run-checks-for [scan-all-files against]
  (do
   (run-git-command ["stash" "--keep-index"])
   (let [[filenames-to-scan
          (if scan-all-files
            (gather-all-filenames)
            (gather-staged-filenames against))]
         [results-of-scan
          (lmap (fn [check] (check-files filenames-to-scan check)) *checks*)]
         [exit-code (derive-max-code results-of-scan)]
         [messages (flatten (derive-message-bodies results-of-scan))]]
     (do
      (for [line messages] (print line))
      (run-git-command ["reset" "--hard"])
      (run-git-command ["stash" "pop" "--quiet" "--index"])
      exit-code))))

(defn get-head-tag []
  (let [[empty-repository-hash "4b825dc642cb6eb9a060e54bf8d69288fbee4904"]
        [(, out err returncode) (get-git-response ["rev-parse" "--verify HEAD"])]]
    (if err empty-repository-hash "HEAD")))

(defmain [&rest args]
  (let [[scan-all-files (and (> (len args) 1) (= (get args 2) "--all-files"))]]
    (sys.exit (int (run-checks-for scan-all-files (get-head-tag))))))

(defmain [&rest args]
  (try
   (let [[optstringsshort 
          (string.join (ap-map (+ (. it [0]) (cond [(. it [2]) ":"] [true ""])) optlist) "")]
         [optstringslong 
          (list (ap-map (+ (. it [1]) (cond [(. it [2]) "="] [true ""])) optlist))]
         [(, opt arg) 
          (getopt.getopt (slice args 1) optstringsshort optstringslong)]
         [rationalize-options 
          (make-options-rationalizer optlist)]
         [options
          (sanify-options (ap-reduce (rationalize-options acc it) opt {}))]]
     

     (cond [(.has_key options "help") (print-help)]
           [(.has_key options "version") (print-version)]
           [true (suggest options)]))
   (catch [err getopt.GetoptError]
     (print (str err))
     (print-help))))

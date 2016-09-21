#!/usr/bin/env hy
(import ConfigParser os subprocess operator re gettext sys getopt)
(.append sys.path "Users/ksternberg/build/git-lint/git_lint_src")
(import [git-lint-options [hyopt]])
(import [git-lint-config [get-config]])

(def _ gettext.gettext)
(def *version* "0.0.2")

(defn tap [a] (print "TAP:" a) a)

                                        ; short-name long-name takes-args description precludes
(def optlist [["o" "only" true (_ "A comma-separated list of only those linters to run") ["exclude"]]
              ["x" "exclude" true (_ "A comma-separated list of linters to skip") []]
              ["l" "linters" false (_ "Show the list of configured linters")]
              ["b" "base" false (_ "Check all changed files in the repository, not just those in the current directory.") []]
              ["a" "all" false (_ "Scan all files in the repository, not just those that have changed.")]
              ["e" "every" false (_ "Short for -b -a: scan everything")]
              ["w" "workspace" false (_ "Scan the workspace") ["staging"]]
              ["s" "staging" false (_ "Scan the staging area (useful for pre-commit).") ["base" "all" "every"]]
              ["g" "changes" false (_ "Report lint failures only for diff'd sections") ["complete"]]
              ["p" "complete" false (_ "Report lint failures for all files") []]
              ["c" "config" true (_ "Path to config file") []]
              ["h" "help" false (_ "This help message") []]
              ["v" "version" false (_"Version information") []]])

(defn get-git-response-raw [cmd]
  (let [[fullcmd (+ ["git"] cmd)]
        [process (subprocess.Popen fullcmd
                                   :universal-newlines True
                                   :stdout subprocess.PIPE
                                   :stderr subprocess.PIPE)]
        [(, out err) (.communicate process)]]
    (, out err process.returncode)))

(defn get-git-response [cmd]
  (let [[(, out error returncode) (get-git-response-raw cmd)]] out))

(defn split-git-response [cmd]
  (let [[(, out error returncode) (get-git-response-raw cmd)]] (.splitlines out)))

(defn split-git-response [cmd]
  (let [[(, out error returncode) (get-git-response-raw cmd)]] (.splitlines out)))


(defn run-git-command [cmd]
  (let [[fullcmd (+ ["git"] cmd)]]
    (subprocess.call fullcmd
                     :stdout subprocess.PIPE
                     :stderr subprocess.PIPE)))

(defn get-shell-response [fullcmd]
  (let [[process (subprocess.Popen fullcmd
                                   :stdout subprocess.PIPE
                                   :stderr subprocess.PIPE
                                   :universal-newlines True
                                   :shell True)]
        [(, out err) (.communicate process)]]
    (, out err process.returncode)))

(def git-base (let [[(, out error returncode)
                     (get-git-response-raw ["rev-parse" "--show-toplevel"])]]
                (if (not (= returncode 0)) None (.rstrip out))))

(defn get-all-from-cwd []
  (split-git-response ["ls-tree" "--name-only" "-r" "HEAD"]))

(defn get-all-from-base []
  (split-git-response ["ls-tree" "--name-only" "-r" "--full-tree" "HEAD"]))

                                        ; Any of these indicate the tree is in a merge
                                        ; conflict state and the user has bigger problems.
(def *merge-conflict-pairs* (set ["DD" "DU" "AU" "AA" "UD" "UA" "UU"]))
(defn get-changed-from-source [trackings]
  (let [[conflicts (filter (fn [t] (t[0:2] in *merge-conflict-pairs*)) trackings)]]
    (if (len conflicts)
      (sys.exit (_ "Current repository contains merge conflicts. Linters will not be run."))
      trackings)))

(defn get-porcelain-status []
  (let [[cmd ["status" "-z" "--porcelain" "--untracked-files=all" "--ignore-submodules=all"]]
        [nonnull (fn [s] (> (len s) 0))]
        [stream (tap (list (filter nonnull (.split (get-git-response cmd) "\0"))))]
        [parse-stream (fn [acc stream]
                        (if (= 0 (len stream))
                          acc
                          (let [[temp (.pop stream 0)]
                                [index (get temp 0)]
                                [workspace (get temp 1)]
                                [filename (tap (slice temp 3))]]
                            (if (= index "R")
                              (.pop stream 0))
                            (parse-stream (+ acc [(, index workspace filename)]) stream))))]]
    (parse-stream [] stream)))

(defn modified-in-workspace [s] (in s[0] ["M" "A" "?"]))
(defn modified-in-staging   [s] (in s[1] ["M" "A"]))
(defn get-name              [s] (s[2]))

                                        ;(defn get-changed-from-cwd []
                                        ;  (->>  (get-changed-from_source (split-git-response ["status" "--porcelain" "--untracked-files=all"]))
                                        ;        (filter (fn [s] (s[0] in 
                                        ;  
                                        ;  (map (fn [s] 
                                        ;  (filter (fn [s] (
                                        ;

(defn get-changed-from-base []
  (get-changed-from_source (split-git-response ["status" "--porcelain" "--untracked-files=all" git-base])))

(defn get-staged-from-cwd []
  ())

(defn gen-staged-from-base []
  ())


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
    (fn [path] (.search matcher path))))

(defn executable-exists [script label]
  (if (not (len script))
    (sys.exit (.format (_ "Syntax error in command configuration for {} ") label))
    (let [[scriptname (get (.split script " ") 0)]
          [paths (.split (.get os.environ "PATH") ":")]
          [isexecutable (fn [p] (and (os.path.exists p) (os.access p os.X_OK)))]]
      (if (not (len scriptname))
        (sys.exit (.format (_ "Syntax error in command configuration for {} ") label))
        (if (= (get scriptname 0) "/")
          (if (isexecutable scriptname)
            scriptname None)
          (let [[possibles (list (filter (fn [path] (isexecutable (os.path.join path scriptname))) paths))]]
            (if (len possibles)
              (get possibles 0)  None)))))))

(defn print-linters [config]
  (print (_ "Currently supported linters:"))
  (for [(, linter items) (.iteritems config)]
    (if (not (executable-exists (.get items "command" "") linter))
      (print (.format "{:<14} {}" linter (_ "(WARNING: executable not found)")))
      (print (.format "{:<14} {}" linter (.get items "comment" ""))))))

(defn git-lint-main [options]
  (print git-base)
  (print (os.path.abspath __file__))
  (let [[config (get-config options git-base)]]
    (print options)
    (print config)
    (print (make-match-filter config))
    (print (get-porcelain-status))))

(defmain [&rest args]
  (if (= git-base None)
    (sys.exit (_ "Not currently in a git repository."))
    (try
      (let [[opts (hyopt optlist args "git lint"
                          "Copyright (c) 2008, 2016 Kenneth M. \"Elf\" Sternberg <elf.sternberg@gmail.com>"
                          "0.0.4")]
            [options opts.options]
            [config (get-config options git-base)]]
        (cond [(.has_key options "help") (opts.print-help)]
              [(.has_key options "version") (opts.print-version)]
              [(.has_key options "linters") (print-linters config)]
              [true (git-lint-main options)]))
      (catch [err getopt.GetoptError]
          (print (str err))
        (print-help)))))

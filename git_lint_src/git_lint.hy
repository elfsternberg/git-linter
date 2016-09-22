#!/usr/bin/env hy  ; -*- mode: clojure -*-
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
              ["s" "staging" false (_ "Scan the staging area (useful for pre-commit).") []]
              ["g" "changes" false (_ "Report lint failures only for diff'd sections") ["complete"]]
              ["p" "complete" false (_ "Report lint failures for all files") []]
              ["c" "config" true (_ "Path to config file") []]
              ["h" "help" false (_ "This help message") []]
              ["v" "version" false (_"Version information") []]])

(defn get-git-response-raw [cmd]
  (let [[fullcmd (+ ["git"] cmd)]
        [process (subprocess.Popen fullcmd
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
                                   :shell True)]
        [(, out err) (.communicate process)]]
    (, out err process.returncode)))

(def git-base (let [[(, out error returncode)
                     (get-git-response-raw ["rev-parse" "--show-toplevel"])]]
                (if (not (= returncode 0)) None (.rstrip out))))

; That mystery number is the precise hash code for a repository for has been initialized,
; but for which nothing has ever been added or committed.  An empty repository has no refs
; at all so you can't use HEAD in this one very rare case.
(def git-head
  (let [[empty-repository-hash "4b825dc642cb6eb9a060e54bf8d69288fbee4904"]
        [(, out err returncode) (get-git-response-raw ["rev-parse" "--verify HEAD"])]]
    (if (not err) "HEAD" empty-repository-hash)))

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
    (fn [path] (print matcher.pattern) (.search matcher path))))

; _    _     _                                 _        _    _          _        _           
;| |  (_)_ _| |_ ___ _ _   _____ _____ __ _  _| |_ __ _| |__| |___   __| |_ __ _| |_ _  _ ___
;| |__| | ' \  _/ -_) '_| / -_) \ / -_) _| || |  _/ _` | '_ \ / -_) (_-<  _/ _` |  _| || (_-<
;|____|_|_||_\__\___|_|   \___/_\_\___\__|\_,_|\__\__,_|_.__/_\___| /__/\__\__,_|\__|\_,_/__/
;                                                                                            

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

; ___ _ _                  _   _       __ _ _ _              
;| __(_) |___   _ __  __ _| |_| |_    / _(_) | |_ ___ _ _ ___
;| _|| | / -_) | '_ \/ _` |  _| ' \  |  _| | |  _/ -_) '_(_-<
;|_| |_|_\___| | .__/\__,_|\__|_||_| |_| |_|_|\__\___|_| /__/
;              |_|                                           

(defn remove-submodules [files]
  (let [[split-out-paths (fn [s] (get (.split s " ") 2))]
        [fixer-re (re.compile "^(\.\.\/)+")]
        [fixer-to-base (fn [s] (.sub fixer-re "" s))]
        [submodule-entries (split-git-response ["submodule" "status"])]
        [submodule-names (map (fn [s] (fixer-to-base (split-out-paths s))) submodule-entries)]]
    (filter (fn [s] (not (in s submodule-names))) files)))

(defn base-file-filter [files]
  (map (fn [f] (os.path.join git-base f)) files))

(defn cwd-file-filter [files]
  (let [[gitcwd (os.path.join (os.path.relpath (os.getcwd) git-base) "")]]
    (base-file-filter (filter (fn [f] (.startswith f gitcwd)) files))))

(defn base-file-cleaner [files]
  (map (fn [f] (.replace f git-base 1)) files))

; ___                __ _ _       _ _    _                                _              
;| _ \__ ___ __ __  / _(_) |___  | (_)__| |_   __ _ ___ _ _  ___ _ _ __ _| |_ ___ _ _ ___
;|   / _` \ V  V / |  _| | / -_) | | (_-<  _| / _` / -_) ' \/ -_) '_/ _` |  _/ _ \ '_(_-<
;|_|_\__,_|\_/\_/  |_| |_|_\___| |_|_/__/\__| \__, \___|_||_\___|_| \__,_|\__\___/_| /__/
;                                             |___/                                      

(def *merge-conflict-pairs* (set ["DD" "DU" "AU" "AA" "UD" "UA" "UU"]))
(defn check-for-conflicts [files]
  (let [[status-pairs (map (fn [(, index workspace filename)] (+ "" index workspace)) files)]
        [conflicts (& (set *merge-conflict-pairs*) (set status-pairs))]]
    (if (len conflicts)
      (sys.exit (_ "Current repository contains merge conflicts. Linters will not be run."))
      files)))

(defn get-porcelain-status []
  (let [[cmd ["status" "-z" "--porcelain" "--untracked-files=all" "--ignore-submodules=all"]]
        [nonnull (fn [s] (> (len s) 0))]
        [stream (list (filter nonnull (.split (get-git-response cmd) "\0")))]
        [parse-stream (fn [acc stream]
                        (if (= 0 (len stream))
                          acc
                          (let [[temp (.pop stream 0)]
                                [index (get temp 0)]
                                [workspace (get temp 1)]
                                [filename (slice temp 3)]]
                            (if (= index "R")
                              (.pop stream 0))
                            (parse-stream (+ acc [(, index workspace filename)]) stream))))]]
    (check-for-conflicts (parse-stream [] stream))))

(defn staging-list []
  (map (fn [(, index workspace filename)] filename)
       (filter (fn [(, index workspace filename)] (in index ["A" "M"])) (get-porcelain-status))))

(defn working-list []
  (map (fn [(, index workspace filename)] filename)
       (filter (fn [(, index workspace filename)] (in workspace ["A" "M" "?"])) (get-porcelain-status))))

(defn all-list []
  (let [[cmd ["ls-tree" "--name-only" "--full-tree" "-r" "-z" git-head]]]
    (filter (fn [s] (> (len s) 0)) (.split (get-git-response cmd) "\0"))))

;   _                     _    _        __ _ _       _ _    _                                _           
;  /_\   ______ ___ _ __ | |__| |___   / _(_) |___  | (_)__| |_   __ _ ___ _ _  ___ _ _ __ _| |_ ___ _ _ 
; / _ \ (_-<_-</ -_) '  \| '_ \ / -_) |  _| | / -_) | | (_-<  _| / _` / -_) ' \/ -_) '_/ _` |  _/ _ \ '_|
;/_/ \_\/__/__/\___|_|_|_|_.__/_\___| |_| |_|_\___| |_|_/__/\__| \__, \___|_||_\___|_| \__,_|\__\___/_|  
;                                                                |___/                                   

(defn pick-filelist-strategy [options]
  (let [[keys (.keys options)]
        [working-directory-trans (if (len (& (set keys) (set ["base" "every"]))) base-file-filter cwd-file-filter)]
        [file-list-generator (cond [(in "staging" keys) staging-list]
                                   [(in "all" keys) all-list]
                                   [true working-list])]]
    (fn [] (working-directory-trans (remove-submodules (file-list-generator))))))

;  ___ _                                                         
; / __| |_  ___  ___ ___ ___   __ _   _ _ _  _ _ _  _ _  ___ _ _ 
;| (__| ' \/ _ \/ _ (_-</ -_) / _` | | '_| || | ' \| ' \/ -_) '_|
; \___|_||_\___/\___/__/\___| \__,_| |_|  \_,_|_||_|_||_\___|_|  
;                                                                

(defn staging-wrapper [run-linters]
  (let [[time-gather (fn [f] (let [[stats (os.stat f)]]
                               (, f (, stats.atime stats.mtime))))]
        [times (list (map time-gather files))]]
    (run-git-command ["stash" "--keep-index"])
    (let [[results (run-linters)]]
      (run-git-command ["reset" "--hard"])
      (run-git-command ["stash" "pop" "--quiet" "--index"])
      (for [(, filename timepair) times]
        (os.utime filename timepair))
      results)))

(defn workspace-wrapper [run-linters]
  (run-linters files))

(defn pick-runner [options]
  (let [[keys (.keys options)]]
    (if (in "s" keys) staging-wrapper workspace-wrapper)))

; __  __      _      
;|  \/  |__ _(_)_ _  
;| |\/| / _` | | ' \ 
;|_|  |_\__,_|_|_||_|
;                    

(defn run-gitlint [options config extras]
  (let [[file-lister (pick-filelist-strategy options)]
        [runner (pick-runner options)]
        [match-filter (make-match-filter config)]
        [lintables (set (filter match-filter (file-lister)))]
        
;        [report-maker (pick-report-maker options)]
;        [linters (pick-linters options config)]]
        ]
    (print (list lintables))))

(defmain [&rest args]
  (let [[opts (hyopt optlist args "git lint"
                     "Copyright (c) 2008, 2016 Kenneth M. \"Elf\" Sternberg <elf.sternberg@gmail.com>"
                     "0.0.4")]]
    (if (= git-base None)
      (sys.exit (_ "Not currently in a git repository."))
      (try
        (let [[options (.get_options opts)]
              [config (get-config options git-base)]]
          (cond [(.has_key options "help") (opts.print-help)]
                [(.has_key options "version") (opts.print-version)]
                [(.has_key options "linters") (print-linters config)]
                [true (run-gitlint options config opts.filenames)]))
        (catch [err getopt.GetoptError]
            (do
              (opts.print-help)))))))

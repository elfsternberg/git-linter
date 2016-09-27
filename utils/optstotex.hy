#!/usr/bin/hy   ; -*- mode: clojure -*-
(import subprocess os sys os.path)

(defn fmit [formatstring iterable]
  (apply .format (+ [formatstring] (list iterable))))

(defmain [&rest args]
  (let [[git_dir (subprocess.check_output ["git" "rev-parse" "--show-toplevel"])]]
    (.append sys.path (os.path.join git_dir "git_lint"))
    (import [git_lint [git_lint]])
    (print (.join "\n" (map (fn [i] (if (get i 2)
                                      (+ (fmit "\item[\oOptArg{{-{0}}}{{ names}} " i)
                                         (fmit "\oOptArg{{--{1}}}={{ names}}] " i)
                                         (fmit "{3}" i))
                                      (+ (fmit "\item[\oOptArg{{-{0}}} " i)
                                         (fmit "\oOptArg{{--{1}}}] " i)
                                         (fmit "{3}" i))))
                            git_lint.OPTIONS_LIST)))))
                
    

; -*- mode: clojure -*-
(import sys os.path gettext ConfigParser)
(def _ gettext.gettext)
        
(defn -find-config-file [options base]
  (if (.has_key options "config")
    (let [[config (get options "config")]
          [configpath (os.path.abspath config)]]
      (if (os.path.isfile configpath)
        configpath
        (sys.exit (.format (_ "Configuration file not found: {}\n") config))))
    (let [[home (os.path.join (.get os.environ "HOME"))]
          [possibles (, (os.path.join base ".git-lint")
                        (os.path.join base ".git-lint/config")
                        (os.path.join home ".git-lint")
                        (os.path.join home ".git-lint/config"))]
          [matches (list (filter os.path.isfile possibles))]]
      (if (len matches) (get matches 0) (sys.exit (_ "No configuration file found"))))))

(defn -load-config-file [path git-base]
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

(defn get-config [options base]
  (-load-config-file (-find-config-file options base) base))

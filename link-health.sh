#!/usr/bin/env bash
wget https://book.servo.org/links.txt
set +e
let ok=0
let warn=0
let error=0
ignore=(
  # Internal GitHub asset link, appears in an example of an error
  # in hacking/web-compat-bugs.md and not meant to be useable.
  https://github.githubassets.com
  # Example of locally hosted WPT tests.
  http://web-platform.test:8000
  # Do not play nice with curl (fake 4XX).
  https://www.researchgate.net
  https://crates.io
  https://developer.huawei.com
  https://gitee.com
)
while IFS= read -r line; do
  link=$( echo "$line" | cut -d":" -f3- )
  for item in "${ignore[@]}"; do
    if [[ $link == $item* ]]; then
      echo "Skipping ignored link $link" >> log.txt
      continue 2
    fi
  done
  # Avoid accidentally DDOSing repeated usages of the same link.
  if [[ $lastlink != $link ]]; then
    status=$( curl -o /dev/null -A "Servo book link health check (https://github.com/servo/book)" -s -w "%{http_code}\n" $link )
  fi
  lastlink=$link
  case ${status:0:1} in
    3)
      echo "WARNING: $status at $line" >> log.txt
      ((++warn))
      ;;
    2)
      echo "OK: $status at $line" >> log.txt
      ((++ok))
      ;;
    *)
      echo "ERROR: $status at $line" >> log.txt
      ((++error))
      ;;
  esac
done < "links.txt"
echo "" >> log.txt
echo "$ok OK, $warn warnings, $error errors" >> log.txt
rm links.txt

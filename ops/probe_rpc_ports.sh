#!/usr/bin/env bash
# External RPC exposure probe for ALL authority RPC ports, including the ones
# outside 9933-9946 that mainnet_health.sh does not test (9947-9963).
# Run from OUTSIDE the hosts. Any reply = exposed to the internet.
probe() {
  ip=$1; shift
  for p in "$@"; do
    r=$(curl -s -m 6 -H 'Content-Type: application/json' \
        -d '{"jsonrpc":"2.0","id":1,"method":"chain_getBlockHash","params":[0]}' \
        "http://$ip:$p" 2>/dev/null)
    if [ -n "$r" ]; then
      echo "EXPOSED $ip:$p -> $(echo "$r" | grep -oP 'result\":\"\K[^\"]{18}')"
    else
      echo "closed  $ip:$p"
    fi
  done
}
probe 185.84.224.91 9944 9945 9955 9960 9961
probe 195.154.80.40 9933 9934 9935 9936 9960 9961
probe 213.136.78.63 9944 9945 9946 9947 9948 9951
probe 5.223.77.19 9960 9961 9962 9963
exit 0

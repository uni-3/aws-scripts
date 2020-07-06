#!/bin/bash

payload=${1:-payload.csv}
content=${2:-text/csv}
topn='{"topn":8}'

#curl --data-binary @${payload} -H "Content-Type: ${content}"  -v http://localhost:8080/invocations
#curl --data-binary @${payload} -H "Content-Type: ${content}" -H "CustomAttributes: ajfeijirje"  -v http://localhost:8080/invocations
curl --data-binary @${payload} -H "Content-Type: ${content}" -H "CustomAttributes: ${topn}"  -v http://localhost:8080/invocations

#!/usr/bin/env bash

LOG_LEVEL=info
start_regular_server=false
start_index_server=false
while [ $# -gt 0 ]; do
    if [ "$1" == "debug" ]; then
        export OPTIMADE_DEBUG=1
        LOG_LEVEL=debug
    elif [ "$1" == "regular" ]; then
        start_regular_server=true
    elif [ "$1" == "index" ]; then
        start_index_server=true
    fi
    shift
done

if [ "$start_regular_server" == "false" ] && [ "$start_index_server" == "false" ]; then
    start_regular_server=true
    start_index_server=true
fi

if [ "$start_regular_server" == "true" ]; then
    MAIN=main
    PORT=5000
    echo ""
    uvicorn optimade.server.$MAIN:app --reload --port $PORT --log-level $LOG_LEVEL &
fi
if [ "$start_index_server" == "true" ]; then
    MAIN=main_index
    PORT=5001
    echo ""
    uvicorn optimade.server.$MAIN:app --reload --port $PORT --log-level $LOG_LEVEL &
fi

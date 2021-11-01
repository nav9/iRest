#!/bin/bash
# Grabs and kill a process from the pidlist that has the word "irest"
#Attribution: https://askubuntu.com/a/99582

pid=`ps aux | grep irest | awk '{print $2}'`
kill -9 $pid

#!/bin/bash

sudo bauerbill -Ss $* --aur-only > packages.txt
$EDITOR packages.txt

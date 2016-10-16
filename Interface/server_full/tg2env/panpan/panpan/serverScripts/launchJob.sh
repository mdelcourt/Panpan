#!/bin/bash
#Arguments : PANPANPATH, SERVERPATH, RESULTSPATH, , NAME
. $1/init.sh
cd $3/$4
$2/panpan/serverScripts/processPanPanModular.py  $4 all >> $3/$4/log.txt 2>&1

#!/usr/bin/env bash

export LC_ALL=C
export TZ=UTC

INPF=urims.txt
OPDIR=/tmp/blocks
TMPF=/tmp/tmp.blk
LINES=`wc -l $INPF | cut -d' ' -f 1`
BLKSIZE=100
PAGECT=$((LINES / BLKSIZE))
PREVH=0000000000000000000000000000000000000000000000000000000000000000

mkdir -p $OPDIR
touch $TMPF

echo "Input:      $INPF"
echo "Output Dir: $OPDIR"
echo "Block Size: $BLKSIZE"
echo "Num Blocks: $PAGECT"

echo "======================"

for i in $(seq 1 $PAGECT)
do
  st=$(($(date +%s%N)/1000000))
  echo "[$st] Generating block $i"
  ll=$((i * BLKSIZE))
  head -$ll $INPF | tail -$BLKSIZE | ./generate_block.py | sed 's/<HASH_OF_PREVIOUS_BLOCK>/sha256:'"$PREVH"'/' | sort > $TMPF
  THISH=`sha256sum $TMPF | cut -d' ' -f 1`
  fsz=`stat --printf="%s" $TMPF`
  modt=`stat --printf="%y" $TMPF | cut -c -19 | sed 's/[-: ]//g'`
  opf=$OPDIR/$modt-$PREVH-$THISH.ukvs
  PREVH=$THISH
  t=$(($(date +%s%N)/1000000))
  echo "[$t] Saving $fsz bytes to $opf"
  mv $TMPF $opf
  t=$(($(date +%s%N)/1000000))
  echo "[$t] Compressing block to $opf.gz"
  gzip $opf
  fsz=`stat --printf="%s" $opf.gz`
  t=$(($(date +%s%N)/1000000))
  echo "[$t] Finished creating block $i of size $fsz bytes in $((t-st)) milliseconds"
  sleep 1
  echo "======================"
done

rm -f $TMPF

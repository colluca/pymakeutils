test1: prereq
	cp $< $@

prereq: preprereq1 preprereq2
	cp $< $@
	cat preprereq2 >> $@

test2: dirprereq

# Regression test for passing `target` as an actual Make goal to `make -pq`
# (rather than only using it to look up its prerequisites in a goal-less
# database dump). `hiddenprereq` is only a prerequisite of `conditional` once
# `conditional` is the requested goal, mirroring a common pattern where an
# auto-generated dependency file is `-include`d only when relevant to
# MAKECMDGOALS. A tool that queries `make -pq` without passing the goal would
# never see `hiddenprereq`.
gendep.mk:
	echo "conditional: hiddenprereq" > $@

-include $(if $(filter conditional,$(MAKECMDGOALS)),gendep.mk)

conditional: standaloneprereq
	cp $< $@
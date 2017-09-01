ncs --stop
rm -rf logs/*
rm -rf state/*
rm -rf ncs-cdb/*
ncs
./test/setup_sim_env.sh

# Ethereum Object Centric Event Logging Framework

A framework able to grab object centric event log (**OCEL**) from Ethereum DApps.

This repository contains two folders:
- **Framework**:
 contains the python code of the framework 
- **Truffle**:
 contains 4 Truffle projects as showcase examples, plus both an input and output folder useful in order to test the framework.

---

## **Tutorials and guide**

### **1. Requirements and set-up**

In order to execute the whole tutorial you need, of course, *python* (>= 3.8) and the *Truffle* suite.
```
sudo apt-get install python
npm install -g truffle
```
Initially, i would suggest you to use *Ganache*, in order to run a local blockchain. It can be downloaded from [here](https://trufflesuite.com/docs/ganache/quickstart/).

Once python is installed in your machine, the framework needs some external packages:
```
pip install -r ./Framework/requirements.txt
```
Moreover, each Truffle project may require to install some javascript dependencies. <br>*For example if you want to deploy contracts using an Infura node. Pay attention, in this case you need also to create a .env file.*<br>
As consequence of that, please go in each truffle project folder and install them, as shown.
```
cd ./Truffle/showcase1
npm install
cd ../..
```
Finally, note that in order to exploit each example, you need to deploy related contracts. Go to the folder of the example you are interested in and then run this command:
```
truffle migrate --reset
```
The previous command will compile and deploy the contracts to a blockchain network, according to your settings in *truffle-config.js*. As consequence of that, i strongly reccomend you to fill this configuration file with your custom parameters. Furthermore, if you are using ganache, as previouly suggested, you need to start it before running this command.

### **2. Gas and deployment analysis:**

- **Deployment costs** can be visualized, looking at the output of the last introduced command. If you want to store it, simply reverse the stdout to file using bash *>*. Some output examples are provided into each truffle project folder, into the *./test/report_migration_output.txt* file.
- **Bytecode sizes**: if you want to check the size of the bytecode run the following command:
```
cat <path_to_json_abi> | jq -r '.deployedBytecode' | wc -c
```
- **Gas cost analysis and contract interactions**: This is one of the most important parts of the tutorial. In order to test the framework you need to populate contract's storage using example function calls. When perfoming this calls, it is useful to save the gas costs required by the related transactions. Fortunately, in the folder *test* of each truffle project, there is a python file, called *report_test.py*, that performs all this stuff, automatically.
```
cd ./Truffle/showcase1/test
python report_test.py > report_test_output.txt
```
Now you can use all the functionalities that the framework provides.

### **3. Framework usage**

In order to perform any interaction with the framework, you have to write down a *manifest* file. Afterwards, you can run the command below.
```
python ./Framework/App.py ./Truffle/input/manifest_1.txt
```

Manifest supports two type of instructions, namely: *definitions* and *commands*. The former are needed to provide a specification of the meta-model (like event-to-object relations, and control-flow constraints), the latter simply tell to the framework what practically it has to do.
Instructions can be inserted in any order, anyway, *definitions* are all instantaneously globally read, and *commands* are executed in the order they are found.
More details can be found in my written thesis report[^1].

Manifest is not compiled and therefore it can throw exceptions at runtime.
Each command is case sensitive and needs to be put in a single line. Blank rows and full-line comments are supported trought the *'%'* keyword.

The following table provides a resume of the available instructions.

| Command list | Parameters |
| --- | --- |
| RUN_GENERATE | <filename> <mode>| 
| RUN_PLOT|  <area> <path> <theme>| 
| RUN_GRAB| <mode> <min_block/freq> <max_block>| 
| RUN_EXPORT|  <format> <filename> <o2o_rel_flag>| 
| RUN_IMPORT|  <path>| 
| RUN_FILTER| 

| Definition list | Parameters| 
| --- | --- |
| DEFINE_CONNECTION | <id> <ip_add> <contract_add> <abi_path>| 
| DEFINE_AREA | <id> <item_0> <item_1> .. <item_n>| 
| DEFINE_CONSTRAINT | <type> <activity_1> <activity_2> <area_id>| 
| DEFINE_LOGIC | <path> <mode>| 
| DEFINE_E2O_REL|  <activity> <type> <min_card> <max_card>| 
| DEFINE_O2O_REL | <obj_type_1> <obj_type_2> <min_card_o1> <max_card_o1> <min_card_o2><max_card_o2>| 

[^1]: If you are interested, please drop me an email.

Examples are the best way to clarify all these concepts. You can find ready-to-use examples of manifest files in the folder *./Truffle/input/**

Finally, if you don't want to lose your time, you can directly access some framework output examples, placed into the folder */Truffle/output/** . These output files refer to the four truffle showcase examples. Inside this directory there are already generated plots, grabbed logs, filtered logs and so on.

I really hope that the framework will be usefull to the community, have a good day! :smile:

---
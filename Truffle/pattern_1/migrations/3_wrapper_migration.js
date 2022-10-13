const wrapper = artifacts.require("./Wrapper.sol");
const contract = artifacts.require("./Contract.sol");

module.exports = function (deployer,network,accounts) {
    deployer.deploy(wrapper, contract.address, {from: accounts[1]} );
}
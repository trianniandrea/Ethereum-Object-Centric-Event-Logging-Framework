const contract = artifacts.require("./Contract.sol");

module.exports = function (deployer) {
    deployer.deploy(contract);
}
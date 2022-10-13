const derived = artifacts.require("Wrapper");
const contract = artifacts.require("Contract");

module.exports = function (deployer) {
    deployer.deploy(derived, contract.address);
}
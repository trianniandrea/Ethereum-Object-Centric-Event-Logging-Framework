const Monolith = artifacts.require("Monolith");

module.exports = function (deployer) {
    deployer.deploy(Monolith);
}
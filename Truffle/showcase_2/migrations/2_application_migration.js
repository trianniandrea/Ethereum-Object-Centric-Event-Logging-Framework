const Application = artifacts.require("Application");

module.exports = function (deployer) {
    deployer.deploy(Application);
}
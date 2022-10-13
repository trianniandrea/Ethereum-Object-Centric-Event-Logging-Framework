const business = artifacts.require("Business");
const logging = artifacts.require("Logging");

module.exports = function (deployer) {
    deployer.deploy(business).then(function() {
        return deployer.deploy(logging, business.address);
    });
}
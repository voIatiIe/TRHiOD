pragma solidity 0.8.18;


contract Manager {
    address private manager;
    address public currentHolder;
    mapping(address => bool) private requestedMarkers;
    uint private addressCounter;

    constructor() payable {
        manager = address(this);
        currentHolder = manager;
        addressCounter = 0;
    }

    receive() external payable {}

    function hasMarker() public view returns (bool) {
        return currentHolder == manager;
    }

    function getCurrentHolder() public view returns (address) {
        return currentHolder;
    }

    function getBalance() public view returns(uint256){
        return address(this).balance;
    }

    function transfer_(uint value) external payable returns (bool) {
        requestedMarkers[msg.sender] = true;
        addressCounter += 1;
        if (hasMarker()) {
            if (value >= 5 wei) {
                currentHolder = msg.sender;
                return true;
            }
        }
        payable(address(msg.sender)).transfer(value);
        return false;
    }

    function returnMarker() public {
        currentHolder = payable(address(this));
    }
}

contract Worker {
    address payable private manager;
    string private lastOpStatus;
    bool private status;

    constructor(address _manager) payable {
        manager = payable(_manager);
        lastOpStatus = "Init";
    }

    function getLastOpStatus() public view returns (string memory) {
        return lastOpStatus;
    }
    
    function getBalance() public view returns(uint256){
        return address(this).balance;
    }

    function hasMarker() public view returns (bool) {
        return Manager(manager).getCurrentHolder() == address(this);
    }

    function requestMarker() public payable {
        if (hasMarker()) {
            lastOpStatus = "Repeat request";
            return;
        }

        if (Manager(manager).hasMarker()) {
            lastOpStatus = "Marker available";

            payable(address(manager)).transfer(5 wei);
            if (Manager(manager).transfer_(5 wei)) {
                lastOpStatus = "Got marker";
            }
            else {
                lastOpStatus = "Low fund";
            }
        }
        else {
            lastOpStatus = "Already taken";
        }
    }

    receive() external payable {}

    function returnMarker() public {
        require(hasMarker(), "No marker to return");
        Manager(manager).returnMarker();
        lastOpStatus = "Released";
    }
}
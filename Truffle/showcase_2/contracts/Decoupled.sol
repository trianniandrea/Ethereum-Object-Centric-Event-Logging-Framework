// SPDX-License-Identifier: CC-BY-SA-4.0
pragma solidity >=0.7.0 <0.9.0;


contract Business{

    struct Ticket{
        uint256 id;
        string class;
        string seat;
        address Traveller_id;
    }

    struct Traveller{
        address id;
        string name;
        string surname;
        string nationality;
    }

    struct Luggage{
        uint256 id;
        string color;
        uint64 weight;
        address Traveller_id;
    }

    struct boarding_card{
        uint256 id;
        uint64 gate;
        uint256 boarding_time;
        address Traveller_id;
        uint256 flight_id;
        bool luggage_delivered;
        bool security_check;
        uint256[] Luggage_id;
        uint256[] Ticket_id;
    }

    struct flight{
        uint256 id;
        string from;
        string to;
        uint256 time_departure;
        uint256 time_arrival;
        string state;
        string company; //possibile altro oggetto se serve
    }

    Ticket[] public tickets;
    boarding_card[] public cards;
    flight[] public flights;
    Luggage[] public luggages;
    mapping (address => Traveller) public travellers;

    function add_flight(string memory from, string memory to, uint256 time_departure, uint256 time_arrival, string memory company) public {
        flights.push(flight(flights.length, from, to, time_departure, time_arrival, "scheduled", company));
    }

    function add_traveller(string memory name, string memory surname, string memory nationality) public {
        travellers[msg.sender] = Traveller(msg.sender, name, surname, nationality);
    }

    function add_luggage(string memory color, uint64 weight, address traveller_id) public {
        luggages.push(Luggage(luggages.length, color, weight, traveller_id));
    }

    function buy_trip (string[] memory class, string[] memory seat, address[] memory travellers) public virtual returns (Ticket[] memory t){
        Ticket[] memory res = new Ticket[](class.length);
        for (uint i = 0; i < class.length; i++) { 
            tickets.push(Ticket(tickets.length, class[i], seat[i], travellers[i]));
            res[i] = tickets[tickets.length-1];
        }
        return res;
    }

    function check_in ( uint256[] memory t, uint64 gate, uint256 boarding_time, address Traveller_id, uint256 flight_id) public virtual returns (boarding_card memory c){
        c.id = cards.length;
        c.gate = gate;
        c.boarding_time = boarding_time;
        c.Traveller_id = Traveller_id;
        c.flight_id = flight_id;
        c.Ticket_id = t;
        cards.push(c);
        return c;
    }

    function deliver_luggage (uint256 card_id, uint256[] memory luggages) public virtual returns (boarding_card memory c){
        cards[card_id].luggage_delivered = true;
        cards[card_id].Luggage_id = luggages;
        return cards[card_id];
    }

    function security_controls (uint256 card_id) public virtual  returns (boarding_card memory c){
        cards[card_id].security_check = true;
        return cards[card_id];
    }

    function start_flight (uint flight_id) public virtual  returns (flight memory f){
        flights[flight_id].state="Departed";
        return flights[flight_id];
    }

    function cancel_flight (uint flight_id) public virtual  returns (flight memory f){
        flights[flight_id].state="Cancelled";
        return flights[flight_id];   
    }
}



contract Logging is Business
{

    Business inner_contract;

    event call_buy_trip (Ticket[] t);
    event call_check_in (boarding_card c);
    event call_deliver_luggage (boarding_card c); //luggage?
    event call_security_control (boarding_card c);
    event call_start_flight (flight f);
    event call_cancel_flight (flight f);

    event update_Luggage(Luggage l);
    event update_Traveller(Traveller t);

    constructor(address add) 
    {
        inner_contract = Business(add);
    }


    function buy_trip (string[] memory class, string[] memory seat, address[] memory travellers) public override returns (Ticket[] memory t){
        t = inner_contract.buy_trip(class, seat, travellers);
        for (uint256 i=0; i<t.length; i++){
            Traveller memory trav;
            (trav.id,trav.name,trav.surname,trav.nationality) = inner_contract.travellers(t[i].Traveller_id);
            emit update_Traveller(trav);
        }
        emit call_buy_trip(t);
    }

    function check_in ( uint256[] memory t, uint64 gate, uint256 boarding_time, address Traveller_id, uint256 flight_id) public override returns (boarding_card memory c){
        c = inner_contract.check_in(t, gate, boarding_time, Traveller_id, flight_id);
        emit call_check_in(c);
    }


    function deliver_luggage (uint256 card_id, uint256[] memory luggages) public override returns (boarding_card memory c){
        c = inner_contract.deliver_luggage(card_id, luggages);
        for (uint256 i=0; i<c.Luggage_id.length; i++){
            Luggage memory l;
            (l.id,l.color,l.weight,l.Traveller_id) = inner_contract.luggages(c.Luggage_id[i]);
            emit update_Luggage(l);
        }
        emit call_deliver_luggage(c);
    }

    function security_controls (uint256 card_id) public override  returns (boarding_card memory c){
        c = inner_contract.security_controls(card_id);
        emit call_security_control(c);
    }

    function start_flight (uint flight_id) public override returns (flight memory f){
        f = inner_contract.start_flight(flight_id);
        emit call_start_flight(f);
    }

    function cancel_flight (uint flight_id) public override  returns (flight memory f){
        f = inner_contract.cancel_flight(flight_id);
        emit call_cancel_flight(f);  
    }

  
}
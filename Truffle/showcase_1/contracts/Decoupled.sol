// SPDX-License-Identifier: CC-BY-SA-4.0
pragma solidity >=0.7.0 <0.9.0;


contract Business {

   struct Order 
   {
        uint256 id;
        uint256 date;
        uint256[] OrderLine_id;
        Customer c;
   }

    struct OrderLine
   {    
        uint256 id;
        Product p;
        uint qty;
        Delivery d;
   }

    struct Product
   {
        string name;
        uint price;
        string[] colori;
   }

    struct Customer
   {
        address id;
        string name;
   }

    struct Delivery
   {
        uint256 id;
        address Customer_id;
        uint256 date;
        string delivery_add;
   }

    mapping (address => Customer) public c;

    Order[] public orders;
    OrderLine[] public orderlines;
    Product[] public p;
    Delivery[] public deliveries;



    function SignUP (string memory name) public {
        c[msg.sender] = Customer(msg.sender, name);
    }

    function addProduct (string memory name, uint price, string[] memory colori) public {
        p.push(Product(name,price,colori));
    }

    function deliveryItems (uint ol_id, address cust,  string memory add) public virtual returns (Delivery memory del){
        deliveries.push(Delivery(deliveries.length, cust, block.timestamp,add));
        orderlines[ol_id].d = deliveries[deliveries.length-1];
        return deliveries[deliveries.length-1];
    }

    function Create_Order(address customer, string memory referreal) public virtual returns (Order memory order)
    {
        order.date = block.timestamp;
        order.c = c[customer];
        order.id = orders.length;
        orders.push(order);
        return order;
    }

    function add_orderline(uint order_id, Product memory prod, uint qty) public {
        OrderLine memory ol;
        ol.qty = qty;
        ol.p = prod;
        ol.id = orderlines.length;
        orderlines.push(ol);
        orders[order_id].OrderLine_id.push(ol.id);

    }

    function pick_item (uint ol_id) public virtual returns (OrderLine memory ol){
        return orderlines[ol_id];
    }

    function wrap_item (uint ol_id, string[] memory notes) public virtual returns (OrderLine memory ol){
        return orderlines[ol_id];
    }


    function getOrdersLength() public view returns(uint count) {
        return orders.length;
    }

    function getOLSfromOrder(uint order_id) public view returns(uint256[] memory ols) {
        return orders[order_id].OrderLine_id;
    }
}

contract Logging is Business
{
    // Deve poter accedere al contratto che deve loggare
    Business inner_contract;

    event call_create_order(Order o, string referreal);
    event call_pick_item(OrderLine ol);
    event call_wrap_item(OrderLine ol, string[] notes);
    event call_delivery_items(Delivery del);
    event update_orderline(OrderLine ol);
    event update_order(Order o);

    constructor(address add) 
    {
        inner_contract = Business(add);
    }

    function Create_Order(address customer, string memory referreal) public override returns (Order memory o)
    {
        o = inner_contract.Create_Order(customer, referreal);
        emit call_create_order(o,referreal);
    }

    function pick_item (uint ol_id) public override returns (OrderLine memory ol)
    {
        ol = inner_contract.pick_item(ol_id);
        emit call_pick_item(ol);

        Order memory o;
        for (uint i = 0; i < inner_contract.getOrdersLength(); i++) 
        {
            uint256[] memory ols = inner_contract.getOLSfromOrder(i);
            for (uint j = 0; j <  ols.length; j++)
            { 
                if ( ols[j] == ol_id)
                {
                    (o.id, o.date, o.c) = inner_contract.orders(i);
                    o.OrderLine_id = ols;
                    emit update_order(o);
                    return ol;
                }
            }
        }
    }


    function wrap_item (uint ol_id, string[] memory notes) public override returns (OrderLine memory ol)
    {
        ol = inner_contract.wrap_item(ol_id, notes);
        
        emit call_wrap_item(ol,notes);
    }


    function deliveryItems (uint ol_id, address cust, string memory add) public override returns (Delivery memory del)
    {
        del = inner_contract.deliveryItems(ol_id, cust, add);

        OrderLine memory ol;
        (ol.id, ol.p, ol.qty, ol.d) = inner_contract.orderlines(ol_id);
        emit call_delivery_items(del);
        emit update_orderline(ol);
    }

}
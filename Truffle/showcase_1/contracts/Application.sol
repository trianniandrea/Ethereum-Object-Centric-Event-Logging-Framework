
contract Application{

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

    function deliveryItems (uint ol_id, address cust,  string memory add) public {
        deliveries.push(Delivery(deliveries.length, cust, block.timestamp,add));
        orderlines[ol_id].d = deliveries[deliveries.length-1];
    }

    function Create_Order(address customer, string memory referreal) public
    {
        Order memory order;
        order.date = block.timestamp;
        order.c = c[customer];
        order.id = orders.length;
        orders.push(order);
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

}
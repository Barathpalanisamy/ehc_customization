## Ehc Customization

## Customizations
### Material Request
Item availability during Material Transfer in Materiaal Request. It ensures that users cannot transfer more items than are available in the specified warehouses, thereby helping to prevent inventory discrepancies.

#### Features
<ul>
    <li>
        Calculates real-time available quantity based on requested quantity for material transfer.
    </li>
    <li>
        Upon validate, the script will automatically validate the available quantity against the requested quantity.
    </li>
    <li>
        If the requested quantity exceeds the available quantity, an error message will be displayed to the user.
    </li>
    <li>
        Users should adjust the quantity or select a different warehouse if necessary before resubmitting.
    </li>
</ul>


### Stock Entry

#### Usage:
<ul>
    <li>
        <b>Creation of Reserve Pick Lists:</b>
        When a document is saved (presumably a Pick List document), the validate function is triggered.
        The create_reserve_picklist function is called to create reserve pick lists based on associated material requests.
        It iterates over the locations (items) in the document and checks if there's a material request item associated with them.
        If there's no existing reserve pick list for the item, it creates a new one with the relevant details.
        Similarly, when a document is saved, the validate function is triggered.
        The update_reserve_pick_list function is called to update the status of reserve pick lists based on changes in associated material requests.
        It checks for material request items associated with the document and compares them with existing reserve pick lists.
            </li>
    <li>
        <b>Updating of Reserve Pick Lists:</b>
If a material request item is removed from the document, the corresponding reserve pick list is marked as cancelled.
    </li>
    <li>
        <b>Ordering Items as per Warehouse: </b>
        The order_items_as_per_warehouse function allows users to order items within the document based on their warehouses.
        It sorts the locations (items) based on the hierarchy of their warehouses.

    </li>
</ul>
</b>

#### Features:
<ul>
    <li>
        <b>Automated Creation of Reserve Pick Lists:</b>
            Simplifies the process of managing inventory by automatically creating reserve pick lists based on associated material requests.
            Ensures that items are reserved for specific documents, helping to prevent overselling or stockouts.
    </li>
    <li>
        <b>Dynamic Update of Reserve Pick Lists:</b>
                Automatically updates the status of reserve pick lists based on changes in associated material requests.
                Ensures that reserve pick lists accurately reflect the current state of material requests.
    </li>
    <li>
        <b>Warehouse-based Ordering of Items:</b>
        Allows users to order items within documents based on their warehouses, facilitating efficient handling and processing of goods.
        Helps streamline warehouse operations by grouping items based on their physical locations.
    </li>
</ul>

## Custom Doctypes
### Reserve Pick List

Reserve Pick List works similarly as a stock ledger entry, but it is used to store the reserved quantity against a picklist, as the picklist is created against a material request.



#### License

MIT

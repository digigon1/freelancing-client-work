const dataset = require('./dataset.json');

const fs = require('fs');

const file = fs.createWriteStream('./data.csv');

file.once('open', () => {
	file.write('name,description,product_type,vendor,brand,thc_percentage,cbd_percentage,strain_type,thc_values,cbd_values,vendor_original,product_weight,product_weight_unit,price,quantity,original_name,version,menu_id,thc_range,cbd_range\n');
	for (var i = 0; i < dataset.length; i++) {
		console.log(i / dataset.length);
		let data = dataset[i];
		for (var j = 0; j < data.menu_row_prices.length; j++) {
			let row = data.menu_row_prices[j];
			file.write((data.name?data.name:'') + ',' + (data.description?data.description:'') + ',' + (data.product_type?data.product_type:'') + ',' + (data.vendor?data.vendor:'') + ',' + (data.brand?data.brand:'') + ',');
			file.write((data.thc_percentage?data.thc_percentage:'') + ',' + (data.cbd_percentage?data.cbd_percentage:'') + ',' + (data.strain_type?data.strain_type:'') + ',' + (data.thc_values?data.thc_values:'') + ',');
			file.write((data.cbd_values?data.cbd_values:'') + ',' + (data.vendor_original?data.vendor_original:'') + ',' + (row.product_weight?row.product_weight:'') + ',');
			file.write((row.product_weight_unit?row.product_weight_unit:'') + ',' + (row.price?row.price:'') + ',' + (row.quantity?row.quantity:'') + ',' + (row.original_name?row.original_name:'') + ',' + (row.version?row.version:'') + ',');
			file.write((row.menu_id?row.menu_id:'') + ',' + (data.thc_range?data.thc_range:'') + ',' + (data.cbd_range?data.cbd_range:''));
		}
		file.write('\n');
	}
	file.end();
})
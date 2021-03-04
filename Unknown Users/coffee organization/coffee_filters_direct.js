function subsetSum(sizes, servings, pricelegend){
	servings = +servings;
	mins = [];
	cost = [];

    cost[0] = 0;
    mins[0] = [];
	for (var i = 1; i < Math.min(...sizes); i++) {
		cost[i] = Number.MAX_VALUE;
		mins[i] = [];
	}

	var i;
	for (i = Math.min(...sizes); i < Math.max(Math.min(...sizes), servings)+1; i++) {
		min = Number.MAX_VALUE;
		s = -1;
		j_chosen = -1;
		for (var j = 0; j < sizes.length; j++) {
			if(min > pricelegend[sizes[j]]+cost[Math.max(i-sizes[j], 0)]){
				j_chosen = j;
				min = pricelegend[sizes[j]]+cost[Math.max(i-sizes[j], 0)];
				s = sizes[j];
			}
		}
		cost[i] = min;
		if(min == Number.MAX_VALUE){
          mins[i] = [];
		} else {
		  t = mins[Math.max(i-sizes[j_chosen], 0)].slice();
		  t.push(sizes[j_chosen]);
		  mins[i] = t;
		  for(var j = 0; j < i; j++){
		  	if(cost[j] == Number.MAX_VALUE){
		  		cost[j] = cost[i];
		  		mins[j] = mins[i];
		  	}
		  }
		}
		if(i == servings && cost[i] == Number.MAX_VALUE){
			servings = servings + 1;
		}
	}
	alert(mins[i-1]);
	return cost[i-1];
}
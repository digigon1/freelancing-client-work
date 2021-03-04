Vue.component('number-input', {
	template: '#number-input',
	props: ['values'],
})

Vue.component('result-set', {
	template: '#result-set',
	props: ['set', 'index'],
	computed: {
		sum: function () {
			return Math.round(this.$root.getSetSum(this.set) * 10)/10;
		},
		results: function () {
			var resultsByNumber = _.map( _.groupBy(this.set), function (o, i) { return { f: o.length, number: i } } )
			
			var resultsByFrequency = _.map( _.groupBy(resultsByNumber, 'f'), function (o, i) {
				if(i == 1){
					var numbers = _.map( o, function (o) { return o.number } )
					var sum = numbers.reduce( function (a, b) { return parseFloat(a) + parseFloat(b) }, 0 )
					var subtotal = sum * i
					return [{
						f: i,
						numbers: _.join( numbers , ' '),
						subtotal: Math.round(subtotal * 10)/10,
						count: numbers.length
					}]
				} else {
					var result = []
					var numbers = _.map( o, function (o) { return o.number } )
					for (var j = 0; j < numbers.length; j++) {
						var sum = numbers[j]
						var subtotal = sum * i
						result.push({
							f: i,
							numbers: numbers[j],
							subtotal: Math.round(subtotal * 10)/10
						})
					}
					return result;
				}
			} )
			// console.log(resultsByFrequency)
			return _.flatten(resultsByFrequency)
		},
	}
})

var app = new Vue({
	el: '#app',
	data: {
		input: [ { f:'', numbers: '' } ],
		setCount: 2,
		precision: 5,
		results: null,
	},
	computed: {
	},
	methods: {
		calculate: function(){
			this.results = []
			var inputElements = document.getElementsByClassName('alg');
			for(var i=0; inputElements[i]; ++i){
			      if(inputElements[i].checked){
			           switch(i){
			           	case 0: this.results.push(this.calculateGreedy()); break;
			           	case 1: this.results.push(this.calculatePPBF()); break;
			           	case 2: this.results.push(this.calculatePPoly()); break;
			           }
			      }
			}
			//console.log(this.results)
		},
		calculateGreedy: function () {

			var stack = [];
			var lines = document.getElementById("input_values").value.split('\n');
			for (var i = 0; i < lines.length; i++) {
				var line = lines[i].split(' ');
				if(line.length == 1)
					stack.push(+line[0]);
				else
					for (var j = 0; j < +line[1]; j++) 
						stack.push(+line[0]);
			}
			stack = stack.sort().reverse();

			var sets = []
			for (var i = 0; i < this.setCount; i++) {
				sets.push([])
			}

			for (var i = 0; i < stack.length; i++) {
				minIndex = this.getMinSetIndex(sets)
				sets[minIndex].push(stack[i])
			}

			return sets;
		},
		calculatePPBF: function () {

			var stack = [];
			var lines = document.getElementById("input_values").value.split('\n');
			for (var i = 0; i < lines.length; i++) {
				var line = lines[i].split(' ');
				if(line.length == 1)
					stack.push(+line[0]);
				else
					for (var j = 0; j < +line[1]; j++) 
						stack.push(+line[0]);
			}
			
			var s = stack.sort().reverse();
			this.stack = s;
			var result = partition(s, this.setCount)
			this.optimizeSets(result)
			return result
		},
		optimizeSets: function (result) {
			var avgSum = this.getAvgSum()
			// console.log(avgSum)

			var finished = false
			var breaker = 0
			var max_swaps = 1

			for (var i = 0; i < result.length; i++) {
				max_swaps *= result[i].length
			}

			console.log(max_swaps)

			do {
				brute_force: {
					for (var i = 0; i < result.length; i++) {
						for (var j = 0; j < result.length; j++) {
							if (i != j) {
								result[i] = result[i].sort()
								result[j] = result[j].sort()
								var sumi = this.getSetSum(result[i])
								var sumj = this.getSetSum(result[j])

								if (sumi != sumj) {
									var diffi = Math.abs( avgSum - sumi )
									var diffj = Math.abs( avgSum - sumj )
									var diff = diffi + diffj

									var indexMin = sumi < sumj ? i : j
									var indexMax = sumi > sumj ? i : j

									for (var k = 0; k < result[indexMin].length; k++) {
										for (var l = result[indexMax].length -1 ; l >= 0 ; l--) {
											if ( ( result[indexMax][l] - result[indexMin][k])  > 0 ) {
												// console.log(result[indexMax][l])
												// console.log(result[indexMin][k])
												// console.log('LOCAL DIF ',  Math.abs( (result[indexMax][l] - result[indexMin][k]) ) * 2 )
												// console.log('SUM DIF ', diff)
												// console.log('-------------------')
												if ( ( Math.abs( (result[indexMax][l] - result[indexMin][k]) ) * 2 ) < diff ) {
													var temp = result[indexMax][l]
													result[indexMax][l] = result[indexMin][k]
													result[indexMin][k] = temp
													// console.log('swapped')
													breaker++
													break brute_force
												}
											}
										}
									}
								}
							}
						}
					}

					finished = true
				}

				if (breaker >= max_swaps) {
					var precise = true
					for (var i = 0; i < result.length; i++) {
						if ( Math.abs( avgSum - this.getSetSum(result[i]) ) > this.precision ) {
							precise = false
						}
					}

					if (precise == true) {
						finished = true
					}
					else {
						// if (breaker >= Math.pow(max_swaps, 2)) {
						// 	finished = true
						// }
						if (breaker >= max_swaps*10) {
							finished = true
						}
					}


				}
			} while (finished == false)
		},
		calculatePPoly: function () {
			var stack = [];
			var lines = document.getElementById("input_values").value.split('\n');
			for (var i = 0; i < lines.length; i++) {
				var line = lines[i].split(' ');
				if(line.length == 1)
					stack.push(+line[0]);
				else
					for (var j = 0; j < +line[1]; j++) 
						stack.push(+line[0]);
			}
			var s = stack.sort().reverse();
			this.stack = s;
			var result = partition(s, this.setCount)
			return result
		},
		getSetSum: function (set) {
			return set.reduce( function (a, b) { return a + b }, 0 )
		},
		getMinSetIndex: function (sets) {
			var minIndex = null;
			var minSum = null;

			for (var i = 0; i < sets.length; i++) {
				var sum = this.getSetSum(sets[i])
				if ( (minSum == null) || ( sum < minSum ) ) {
					minIndex = i
					minSum = sum
				}
			}

			return minIndex
		},
		getAvgSum: function () {
			return this.getSetSum(this.stack) / this.setCount
		},
	},
	mounted () {
	},
})


var partition = function(seq, k) {
  if(k === 0) return []
  if(k === 1) return [seq]
  if(k >= seq.length) {
	// return the lists of each single element in sequence, plus empty lists for any extra buckets.
	var repeated =  []
	for(var q = 0; q < k - seq.length; ++q) repeated.push([])
	return seq.map(function(x) {return [x]}).concat(repeated)
  }

  var sequence = seq.slice(0)
  var dividers = []
  var sums = prefixSums(sequence, k)
  var conds = boundaryConditions(sequence, k, sums)

  // evaluate main recurrence
  for(var i = 2; i <= sequence.length; ++i) {
	for(var j = 2; j <= k; ++j) {
	  conds[i][j] = undefined
	  for(var x = 1; x < i; ++x) {
		var s = Math.max(conds[x][j-1], sums[i] - sums[x])
		dividers[i] = dividers[i] || [] // Initialize a new row in the dividers matrix (unless it's already initialized).
		// Continue to find the cost of the largest range in the optimal partition.
		if(conds[i][j] === undefined || conds[i][j] > s) {
		  conds[i][j] = s
		  dividers[i][j] = x
		}
	  }
	}
  }
  return(reconstructPartition(sequence, dividers, k))
}

// Work our way back up through the dividers, referencing each divider that we
// saved given a value for k and a length of seq, using each divider to make
// the partitions.
var reconstructPartition = function(seq, dividers, k) {
  var partitions = []
  while (k > 1) {
	if(dividers[seq.length]) {
	  var divider = dividers[seq.length][k]
	  var part = seq.splice(divider)
	  partitions.unshift(part)
	}
	k = k - 1
  }
  partitions.unshift(seq)
  return partitions
}

// Given a list of numbers of length n, loop through it with index 'i'
// Make each element the sum of all the numbers from 0...i
// For example, given [1,2,3,4,5]
// The prefix sums are [1,3,6,10,15]
var prefixSums = function(seq) {
  var sums = [0]
  for(var i = 1; i <= seq.length; ++i) {
	sums[i] = sums[i - 1] + seq[i - 1]
  }
  return sums
}

// This matrix holds the maximum sums over all the ranges given the length of
// seq and the number of buckets (k)
var boundaryConditions = function(seq, k, sums) {
  var conds = []
  for(var i = 1; i <= seq.length; ++i) {
	conds[i] = []
	conds[i][1] = sums[i]
  }
  for(var j = 1; j <= k; ++j) conds[1][j] = seq[0]
  return conds
}
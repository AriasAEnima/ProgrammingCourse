
function addElement(array, element) {
    array.push(element);
}

function addElement2(array, element) {
    const l = []
    for (e of array) {
        l.push(e);
    }
    l.push(element);
    return l;
}


// Multiparadigma
// map , reduce , filter , forEach , flatmap , every , some , find , findIndex

// Inmutable

// Mutable
let array = [1, 2, 3, 4, 5];

// int[]
// List<Integer>

function main() {
    //addElement(array, 2)
    //console.log(array); // [1, 2, 3, 4, 5, 2]
    const v2 = addElement2(array, 7)
    array = v2
    const element = {name: "Juan", age: 20}
    addElement(array,element)
    const v3 = addElement2(array, 7)
    console.log(array); 
    console.log(v3); 
    element.name = "Pedro"
    console.log(array); 
    console.log(v3); 
}

// return nil 

function addElement(array, element) {
    array.push(element);
}


function addElement3(array, element) {
    const l = []
    for (e of array) {
        l.push(e);
    }
    l.push(element);
}

console.log(addElement3([1, 2, 3], 4)); // [1, 2, 3, 4]

// Map<String, String>  // [[k v] , [k v]]
// .map()
// map :  List => List 
//         # e = # e 

function myMapImpl(array, fn) {
    const l = []
    for (e of array) {
        l.push(fn(e));
    }
    return l;
}
// anonymous function
// (myVarName) => myOperation
// (e) => e * 2 

function multiplyBy2(e) {
    return e * 2;
}

console.log(myMapImpl([1, 2, 3], (e)=> e*2)); // [2, 4, 6]

console.log(myMapImpl([1, 2, 3], multiplyBy2 )); // [2, 4, 6]


function myMap(array, fn) {
    return array.map(fn);
}
const lmap = [1, 2, 3]
//console.log(myMap(lmap, multiplyBy2));
//console.log(myMapImpl(lmap, multiplyBy2 )); // [2, 4, 6]
//console.log(lmap)

function printElements(l){  
    if (l.length == 0) {
        return;
    } 
    console.log(l[0]);
    printElements(l.slice(1));   
}

printElements(lmap) // [1, 2, 3]
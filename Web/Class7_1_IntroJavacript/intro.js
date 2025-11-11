// Declare

var foo = 4;
var bar = "other" // ; optional but is well practice use it
let number = 3; 
const pi = 3.1416;
// let number = 5;
// pi = 2.4;}

// AND
console.log( true && false)
// OR
console.log( true || false)
// ==
console.log( true == false)
// != 
console.log( true != false)

// If sentence
if (foo > 4){
    console.log("Is greater than 4")
}else if(foo == 4) {
    console.log("Is equal 4")
}else {
    console.log("Is lower than 4")
}

// Lists
const list = [];
list.push("Red")
list.push("White")
console.log(`First element list : ${list[0]}`) // Get an element
// list = ["A"] not allow change the reference

// Function
function myFunction(name){
    // Reverse ` and place holder ${} 
    console.log(`Hello ${name}, How are you ${name}?`);
}
myFunction("Eduardo")

// By value
let n = 0
function add(n,times){
    for (let i= 1; i<= times; i++){
        n = n +1;
    }    
    console.log(`N inside add fun ${n}`);
    return n;
}
add(n, 20)
console.log(`N after call fun ${n}`)

// By reference
const listNames = ["Eduardo", "Carlos"];

function addNames(list,newName){
    listNames.push(newName);
}
addNames(listNames,"Camila");
console.log(`listNames after call fun ${listNames}`);

let j = "";
while(j!="AAA"){
    console.log("While j", j);
    j = j+"A"
}

// For sentence
for(let i= 0; i<=10 ; i= i+1){
    console.log("For :", i)
}
// Let scope , is not possible
// console.log(i)
// other for using list as index in
for (index in listNames){
    console.log(`Index of list: ${index}, 
        element of the list ${listNames[index]}`)
} 
// direct element
for (const element of listNames){
    console.log(`Element of list ${element}`)
}
// print list with limits
for (let i = 0; i<listNames.length ; i++){
    console.log(`Elemento ${i}, ${listNames[i]}`)
}





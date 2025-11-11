
const lista = [1, 2, 3, 4, 5];

// console.log(lista.map( (e)=> e*2))
// console.log(lista)

const myMap = {"edad" : 20, "nombre": "Juan", "apellido": "Perez"};

// console.log(Object.keys(myMap));

const myMapKeys = Object.keys(myMap);

myMapKeys.map( (k) => { 
    const value = myMap[k] // valor de cada llave
    myMap[k] = value.toString().toUpperCase();
} )

// console.log(myMap);

console.log( lista.reduce( (acc, e) => {
    return acc + e;
}, 0));

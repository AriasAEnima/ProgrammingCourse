// JSON
const dev = {
  name: "Eduardo",
  lastName: "Arias",
  age: 28,
  contactInfo: {
    phone: 3000000,
    email: "julianeduardoarias@outlook.com",
  },
  experience: {
    languages: ["Python", "Scala", "Clojure", "Java"],
  },
};

const devs = [dev, { name: "Camila", experience: {languages: ["Typescript", "Angular"] }}];
// Access data, root properties
console.log(`Name: ${dev.name}`);
console.log(`Contact Info: ${dev.contactinfo}`); // It's case sensitive !!!
console.log(`Contact Info: ${dev.contactInfo}`); // Is a object print
console.log(`Contact Info: ${JSON.stringify(dev.contactInfo)}`); // Force to cast to String
console.log(`Email: ${dev.contactInfo.email}`); // Nested basic type
console.log(`Language 1: ${dev.experience.languages[1]}`); // Get a element of nested array

// Unpack / Destruct  use {} as multiple assigns
const age1 = dev.age;
const name1 = dev.name
const {name, age, experience} = dev;
console.log(`Eduardo age : ${age} Eduardo experience: ${JSON.stringify(experience)}`)

// Access of root object array
console.log(`Camila experience: 
  ${JSON.stringify(devs[1].experience)}`); // Get a array from array, (dont show a [])

// Spread ... unpack and add the elements
devs[1].experience = 
        {...devs[1].experience, 
            technologies: ["SQL", "Grafana"]}
console.log(`Camila experience after:
     ${JSON.stringify(devs[1].experience)}`);  

dev.contactInfo = { ...dev.contactInfo, githubUser: "AriasAenima"}
console.log(`Eduardo contact after:
    ${JSON.stringify(devs[0].contactInfo)}`);  

// Ternary
const newUser = false;
const result = newUser ? "Hello User" : "Hello User again!";
console.log(result)

// Function arrow
function foo(a,b){
    return a+b
}
const bar = (a,b)=> a + b;
// what happen if you dont use parameter and () ? 
console.log(foo)
console.log(bar)
console.log(foo(2,3))
console.log(bar(2,4))

// Default values
function baz(n , name = "Eduardo"){
    for (let i=1; i<=n ; i++){
        console.log(`Hello ${name}`)
    }
}
baz(3)
baz(2,"Amanda")

// Anonimus function 
function functionThatExecuteFunction(n , t, f){
    let ans = n;
    for (let i = 1; i<=t ; i++){
      ans = f(ans)
    }
    return ans;
}

console.log(functionThatExecuteFunction( 100, 3, (e)=> e/2 ))
console.log(functionThatExecuteFunction( 2 , 3 , (e)=> e*e))
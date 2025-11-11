
val myList: List[String] = List("Ivan", "Eduardo", "Juan")

myList.map( (s: String) => s.toUpperCase())

val myMap = Map(
  "Ivan" -> 25,
  "Eduardo" -> 30,
  "Juan" -> 35
)

def mapFunction[A, B](mapRegister: (A, Int)) = {
  (mapRegister._1, mapRegister._2 + 2)
}

myMap.map(
  (mapRegister: (String, Int))
  => (mapRegister._1, mapRegister._2 + 2) )
// ""
myList.reduce( (s1: String, s2: String) => s1 + ", " + s2)

val myList2 = List(1, 2, 3, 3, 4, 4)

// 0
myList2.reduce( (s1: Int, s2: Int) => s1 + s2)

myList2.filter( (s: Int) => s >= 3)


myList2.reduce( (s1: Int, s2: Int) => 
                 if (s2 >= 3){
                   s1 + s2
                 } else {
                   s1
                 } )

// 1
myList2.reduce(  (acc: Int , n: Int) => acc*n)

val foldProductV1= myList2.foldLeft(0){ 
  (acc: Int, n: Int) => acc*n
}

val foldProductV2= myList2.foldLeft(1){
  (acc: Int, n: Int) => acc*n
}

val myMap2 = Map(
  "Ivan" -> 25,
  "Eduardo" -> 30,
  "Juan" -> 35
)

myMap2.reduce( 
  (s1: (String, Int), s2: (String, Int)) => 
    if (s2._2 >= 30) {
      // Concatenar nombres , // y sumar edades
      (s1._1 + ", " + s2._1, s1._2 + s2._2)
    } else {
      (s1._1, s1._2)
    }
)

myMap2.foldLeft(("",0)){
  (s1: (String, Int), s2: (String, Int)) =>
    if (s2._2 >= 30) {
      // Concatenar nombres , // y sumar edades
      (s1._1 + ", " + s2._1, s1._2 + s2._2)
    } else {
      (s1._1, s1._2)
    }
}


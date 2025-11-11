import scala.annotation.tailrec

def addElement(e: Int, list: List[Int] ): List[Int] = {
  val newList = list :+ e
  newList
}

@tailrec
def printlnElements(list: List[Int]): Unit = {
  println(list.head)
  if (Nil != list.tail) {
    printlnElements(list.tail)
  }
}

@tailrec
def forEachImpl[A](list: List[A], f: A => Unit): Unit = {
  f(list.head)
  if (Nil != list.tail) {
    forEachImpl(list.tail, f)
  }
}

@tailrec
def forMapImpl[A, B](list: List[A], f: A => B, accu: List[B]): List[B] = {
  if (Nil != list.tail ){
    forMapImpl(list.tail, f, accu :+ f(list.head))
  }else{
    accu :+ f(list.head)
  }
}

@tailrec
def reduceImpl[A](list: List[A], f: (A,A) => A, accu: A): A = {
  if (list.tail == Nil ) {
    f(accu,list.head)
  } else {
    reduceImpl(list.tail, f, f(list.head,accu))
  }
}

@tailrec
def reduceImplClass[A, B](list: List[A], f: (A,B) => B, accu: B): B = {
  if (list.tail == Nil ) {
    f(list.head, accu)
  } else {
    reduceImplClass(list.tail, f, f(list.head,accu))
  }
}

val list : List[(String, Int)] = List(
  "edad" -> 25,
  "edad" -> 25,
  "edad" -> 25
)

@tailrec
def reduceImplMap[A, B, C](map: Map[A, B], f: ((A,B),C) => C, accu: C): C = {
  if (map.isEmpty ) {
    accu
  } else {
    val firstEntry = map.head // Devuelve un par (K, V)
    val restMap = map.tail // Devuelve el resto del mapa
    reduceImplMap(restMap, f, f(firstEntry, accu))
  }
}

// val list = List(1,2,3)
// reduceImpl(list , (x: Int, y: Int) => x + y, 0)

val usuarios = Map( "Juan" -> Map("edad" -> 25, "estatura"-> 20),
                    "María" -> Map("edad" -> 30),
                    "Carlos" -> Map("edad" -> 45))


reduceImplMap(usuarios ,
  (x: (String, Map[String , Int]), y: Int)=>
    val (nombre, datos) = x
    y + datos("edad")
  , 0  )

reduceImplMap(usuarios ,
  (x: (String, Map[String , Int]), y: String)=>
    val (nombre, datos) = x
    y + " "+ nombre
  , ""  )

def forMapInit[A, B, C](map: Map[A, B], f: ((A, B)) => C): List[C] = {
  @tailrec
  def forMapImplMap(map: Map[A, B], f: ((A, B)) => C, accu: List[C]): List[C] = {
    if (map.isEmpty) {
      accu
    } else {
      val firstEntry = map.head // Devuelve un par (K, V)
      val restMap = map.tail // Devuelve el resto del mapa
      forMapImplMap(restMap, f, accu:+f(firstEntry))
    }
  }
  forMapImplMap(map, f , List())
}

forMapInit(usuarios ,
  (nombre: String, v: Map[String , Int]) =>
    nombre)


reduceImplMap(usuarios ,
  (x: (String, Map[String , Int]), y: List[String]) =>
    val (nombre, datos) = x
    y :+ nombre
  , List())

package dsl

import scala.util.parsing.combinator._
import scala.util.matching.Regex
import com.ning.http.client._
import scala.concurrent.Future

case class Person(name : String)
case class TwitterDetails(number : Int, greaterThan : Int = 0)
case class NumberTweets(number : Int)
case class FollowerLimit(greaterThan : Int)

 object Aggregation extends Enumeration {
  type Aggregation = Value
  val min, max, avg = Value
  
 }

object Operation extends Enumeration {
  type Operation = Value
  val positive, negative, both = Value
  
 }
import Operation._
import Aggregation._
case class Operations(ops : List[Operation])

case class RequestObject(person : Person, numberTweets : NumberTweets, followerLimit : FollowerLimit, 
    operation : Operation, aggregation : Aggregation){
  
    def makeURL = {
      val str = "person=%s&followers=%d&tweets=%d&class=%s&aggregation=%s" format (person.name, followerLimit.greaterThan,
          numberTweets.number, operation.toString, aggregation.toString)
          
       str
      
    }
}

class SentimentAnalysisLanguage extends RegexParsers {
    override val skipWhitespace = false
    
     def number : Parser[Int] = """[0-9]+""".r ^^ {_.toInt}
     def space : Parser[Any] = """\s""".r
     
     def twitterUsername : Parser[String] = """[a-zA-Z0-9]+""".r
     
     def numberTweets : Parser[String] = "get" ~> space ~> number <~ space <~ "tweets" <~ space ^^ {
       case number => number.toString
     }
     
     def person : Parser[String] = "of" ~> space ~> twitterUsername ^^ {
       case twitterUsername => twitterUsername.toString
     }
     
     def followerLimit : Parser[String] = "if" ~> space ~> "followers" ~> space ~> "greater" ~> space ~> "than" ~> space ~> number <~ "." ^^ {
       case number => number.toString
     }
    
      def tweetsAndPerson : Parser[List[String]] = numberTweets ~ person <~ "." ^^ {
       case numberTweets ~ person => List(numberTweets, person)
      
     } 
      
      def tweetsAndPersonAndLimit : Parser[List[String]] = tweetsAndPerson ~ opt(space ~ followerLimit) <~ space ^^ {
        case tweetsAndPerson ~ followerLimit => List(tweetsAndPerson(0), tweetsAndPerson(1), followerLimit.toString)
      }
      
      
      def aggregation : Parser[String] = "max" | "min" | "avg"
      
      def tweetClass : Parser[String] = "positive" | "negative" | "both"
      
      def secondPart : Parser[List[String]] = "Find" ~> space ~> aggregation ~ space ~ "of" ~ space ~ tweetClass <~ space <~ "tweets." ^^ {
        case aggregation ~ tweetClass ~ c  ~ d => List(aggregation._1, d)
      }
      
      def all : Parser[List[String]] = tweetsAndPersonAndLimit ~ secondPart ^^ {
        // not very pretty, will change. sorry needed to get it done
        case a ~ b => List(a(0), a(1), a(2), b(0), b(1))
      }
     def apply(expr : String) = parseAll(all, expr)

}



   
object Main {
  
  def makeHTTPCall(req : RequestObject)  = {
    val client = new AsyncHttpClient
    val str = "http://127.0.0.1:5000/predict?%s" format (req.makeURL)
     val response = client.prepareGet(str).execute.get
    if(response.getStatusCode < 400){
      println(response.getResponseBody)
      
    }
  }

  def main(args: Array[String]): Unit = {
  
   
    val text = "get 2 tweets of 1adityajoshi. if followers greater than 30. Find min of negative tweets."
    val parser = new SentimentAnalysisLanguage
    val results = parser(text).get
    val a = results(2)
    val numPattern = new Regex("[0-9]+")
  
    var result = 0
    for(res <- numPattern.findAllIn(a)) result = res.toInt   // Yes I know.
    
    val reqObject = RequestObject(Person(results(1)), NumberTweets(results(0).toInt), FollowerLimit(result), 
        Operation.withName(results(4)), Aggregation.withName(results(3)))
    makeHTTPCall(reqObject)
  
  }

  
}
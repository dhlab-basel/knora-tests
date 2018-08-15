import sbt._
import Keys._

// Create a new MergeStrategy for aop.xml files
// from https://github.com/kamon-io/Kamon/blob/master/kamon-examples/kamon-autoweave-example/build.sbt#L28-L62
// https://stackoverflow.com/questions/39554672/aspectjweaver-with-fat-jar
val aopMerge = new sbtassembly.MergeStrategy {
  val name = "aopMerge"
  import scala.xml._
  import scala.xml.dtd._

  def apply(tempDir: File, path: String, files: Seq[File]): Either[String, Seq[(File, String)]] = {
    val dt = DocType("aspectj", PublicID("-//AspectJ//DTD//EN", "http://www.eclipse.org/aspectj/dtd/aspectj.dtd"), Nil)
    val file = MergeStrategy.createMergeTarget(tempDir, path)
    val xmls: Seq[Elem] = files.map(XML.loadFile)
    val aspectsChildren: Seq[Node] = xmls.flatMap(_ \\ "aspectj" \ "aspects" \ "_")
    val weaverChildren: Seq[Node] = xmls.flatMap(_ \\ "aspectj" \ "weaver" \ "_")
    val options: String = xmls.map(x => (x \\ "aspectj" \ "weaver" \ "@options").text).mkString(" ").trim
    val weaverAttr = if (options.isEmpty) Null else new UnprefixedAttribute("options", options, Null)
    val aspects = new Elem(null, "aspects", Null, TopScope, false, aspectsChildren: _*)
    val weaver = new Elem(null, "weaver", weaverAttr, TopScope, false, weaverChildren: _*)
    val aspectj = new Elem(null, "aspectj", Null, TopScope, false, aspects, weaver)
    XML.save(file.toString, aspectj, "UTF-8", xmlDecl = false, dt)
    IO.append(file, IO.Newline.getBytes(IO.defaultCharset))
    Right(Seq(file -> path))
  }
}

lazy val commonSettings = Seq(
  organization := "org.knora",
  version := "0.0.1-SNAPSHOT",
  scalaVersion := "2.12.6",
  scalacOptions ++= Seq("-unchecked", "-deprecation"),
  test in assembly := {},
  assemblyMergeStrategy in assembly := {
    case m if m.toLowerCase.endsWith("manifest.mf") => MergeStrategy.discard
    case m if m.toLowerCase.matches("meta-inf.*\\.sf$") => MergeStrategy.discard
    case m if m.toLowerCase.matches("meta-inf.*\\.properties") => MergeStrategy.discard
    case PathList("META-INF", "aop.xml") => aopMerge
    case PathList(ps @ _ *) if ps.last endsWith ".txt.1" => MergeStrategy.first
    case "reference.conf" => MergeStrategy.concat
    case "application.conf" => MergeStrategy.concat
    case x =>
      val oldStrategy = (assemblyMergeStrategy in assembly).value
      oldStrategy(x)
  }
)

lazy val perftests = (project in file("perftests"))
  .enablePlugins(GatlingPlugin)
  .settings(
    scalaVersion := "2.12.6",
    libraryDependencies ++= Seq(
      "org.scalatest" %% "scalatest" % "3.0.4" % "test,it",
      "io.gatling.highcharts" % "gatling-charts-highcharts" % "2.3.1" % "test,it",
      "io.gatling" % "gatling-test-framework" % "2.3.1" % "test,it"
    )
  )

scalafmtConfig in ThisBuild := Some(file(".scalafmt.conf"))
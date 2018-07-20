package org.knora.perftests

import io.gatling.core.Predef.{forAll, rampUsers, scenario}
import io.gatling.core.Predef._
import io.gatling.core.structure.ScenarioBuilder
import io.gatling.http.Predef._

import scala.concurrent.duration._

class GetUsersSimulation extends BaseSimulation {

  val userScenario: ScenarioBuilder = scenario("Get users scenario")
    .exec(http("get users").get("/admin/users"))

  setUp(
    userScenario
      .inject(rampUsers(100) over(1 minute) )
      .protocols(httpConf))
    .assertions(forAll.failedRequests.percent.is(0))
}
/*
 * Copyright © 2015-2018 the contributors (see Contributors.md).
 *
 *  This file is part of Knora.
 *
 *  Knora is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Affero General Public License as published
 *  by the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  Knora is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Affero General Public License for more details.
 *
 *  You should have received a copy of the GNU Affero General Public
 *  License along with Knora.  If not, see <http://www.gnu.org/licenses/>.
 */

package org.knora.perftests.stress

class StressSimulation extends Simulation {

  val localhostURL = "http://localhost:3333"

  val httpConf: HttpProtocolBuilder = createHttpConf(localhostURL)

  val host1HttpConf: HttpProtocolBuilder = createHttpConf("http://192.168.69.100:9000")
  val host2HttpConf: HttpProtocolBuilder = createHttpConf("http://192.168.69.101:9000")

  private def createHttpConf(baseUrl: String) =
    http
      .baseURL(baseUrl)
      .acceptHeader("application/json, text/html, text/plain, */*")
      .acceptEncodingHeader("gzip, deflate")

  val userCreationChain: ChainBuilder = exec(
    http("create user")
      .post("/user")
      .check(status.is(201))
      .check(saveUserId))
    .exec(http("get user").get("/user/${userId}").check(status.is(200)))

  private def saveUserId = {
    regex("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}").saveAs("userId")
  }
}
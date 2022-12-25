#[macro_use] extern crate rocket;

use log::{info, error};
use rocket_db_pools::{Database, Connection};
use rocket_db_pools::deadpool_postgres::{Pool, ClientWrapper};
use rocket::response::status;
use std::fmt;
use rocket::http::Status;

#[derive(Database)]
#[database("food_db")]
struct FoodDb(rocket_db_pools::deadpool_postgres::Pool);

#[get("/")]
fn index() -> &'static str {
    "Hello, world!"
}

#[get("/<user_id>")]
async fn get_click(mut db: Connection<FoodDb>, user_id: i32) -> (Status, String) {
    let sql_result = db.query_opt("SELECT click_count from clicks where user_id=$1", &[&user_id])
        .await;

    if sql_result.is_err() {
        return (Status::InternalServerError, String::from("Error occured"));
    }

    let sql_row = sql_result.unwrap();

    if sql_row.is_none() {
        return (Status::NotFound, format!("No user found with ID: {}", user_id));
    }

    let click_count: i32 = sql_row.unwrap().get(0);

    return (Status::Ok, format!("User ID {} clicked {} times", user_id, click_count));
}

#[post("/<user_id>")]
async fn click(mut db: Connection<FoodDb>, user_id: i32) -> (Status, String) {
    let sql_result = db.query_one("INSERT into clicks (user_id, click_count) VALUES ($1, 1) ON conflict(user_id) DO UPDATE set click_count = clicks.click_count + 1 where clicks.user_id=$1 returning click_count",
                        &[&user_id])
        .await;

    if sql_result.is_err() {
        error!("Error occured in SQL: {}", sql_result.err().unwrap());
        return (Status::InternalServerError, String::from("Error occured"));
    }

    let click_result: i32 = sql_result.unwrap().get(0);

    return (Status::Ok, format!("Clicks for User ID {}: {}", user_id, click_result));
}

#[launch]
fn rocket() -> _ {
    rocket::build()
        .attach(FoodDb::init())
        .mount("/", routes![index])
        .mount("/click", routes![get_click, click])
}
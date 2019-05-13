extern crate pyo3;

mod subsplit;

use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};
use pyo3::wrap_pyfunction;
use std::str;
use subsplit::split_at_first;

/// Split a raw IRCv3 line into usable Python types.
///
/// Provided a `bytes` message in IRCv3 format, breaks it down into a Tuple.
/// Tuple contains:
///     Prefix - str
///     Command - str
///     Arguments - list
///     Trailing - str
///     IRCv3 Tags - dict
///
/// Input: `bytes`
/// Return: `Tuple[str, str, List[str], str, dict]`
#[pyfunction]
fn decode(input: &PyBytes) -> PyResult<(&str, &str, Vec<&str>, &str, PyObject)> {
    // First, decode the data into something we can work.
    let raw_str: &str = str::from_utf8(input.as_bytes())?;

    // Then, initialize the Output Structures.
    let gil: GILGuard = Python::acquire_gil();
    let py: Python = gil.python();
    let tags_dict: &PyDict = PyDict::new(py);
    let mut message: &str;

    // Third, break the line down.
    if raw_str.starts_with('@') {
        // The Tags String is the first half of the original message received by IRC. The "regular"
        //  message begins after the first space.
        let (tag_str, msg_str) = split_at_first(&raw_str[1..], " ");
        message = msg_str;

        // Break the tagstr into a Split Iterator. Spliterator?
        let tags_str_iter = tag_str.split(';');

        // Loop through the Spliterator of pair strings, and break each one the rest of the way
        //  down. Add values to the Dict.
        for kvp in tags_str_iter {
            if !kvp.is_empty() {
                let (key, val) = split_at_first(kvp, "=");
                if !key.is_empty() {
                    tags_dict.set_item(key, val)?;
                }
            }
        }
    } else {
        // There are no tags. This is pure message.
        message = raw_str;
    }

    // Now, parse the message itself.
    // This format is specified in Section 2.3.1 of RFC 1459.
    let prefix: &str;
    if message.starts_with(':') {
        // This Message has a Prefix. The Prefix is most likely hostname and/or server info. It ends
        //  at the first space.
        let (a, b) = split_at_first(&message[1..], " ");
        prefix = a;
        message = b;
    } else {
        // There is no Prefix.
        prefix = "";
    }

    // The trailing data is found after a space and a colon. Everything up to that point is the IRC
    //  Command and any Arguments passed to it.
    let (cmd_and_args, trail) = split_at_first(message, " :");

    // The Command is the first word before any Arguments.
    let (command, args_str) = split_at_first(cmd_and_args, " ");

    // The Arguments should be split apart into a List.
    let arguments = args_str.split_ascii_whitespace();

    // Compile everything into a Tuple, and send it back up to Python.
    let output = (
        prefix,
        command,
        arguments.collect(),
        trail,
        tags_dict.into(),
    );
    Ok(output)
}

/// A module for manipulation of IRCv3 data.
#[pymodule]
fn ircrust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(decode))?;

    Ok(())
}

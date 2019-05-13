pub fn split_at_first<'a>(line: &'a str, at: &'a str) -> (&'a str, &'a str) {
    match line.find(at) {
        Some(idx) => (&line[..idx], &line[idx + at.len()..]),
        None => (line, ""),
    }
}

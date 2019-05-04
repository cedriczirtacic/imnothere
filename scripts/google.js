q = document.getElementsByClassName("gLFyf gsfi");
if (q.length > 0) {
    q[0].value = "test";
    while (document.readyState != 'complete')
        ;
    document.forms[0].submit();
}
return true;

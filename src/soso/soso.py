def hello_world(message, emphasize):
    """Prints a message to the world!

    Parameters
    ----------
    message : str
        The message to print.
    emphasize : bool
        Whether to emphasize the message.

    Returns
    -------
    str
        The message.

    Notes
    -----
    This function is not very useful. Or is it?
    """
    if emphasize:
        return message + "!"
    else:
        return message


class Commands(dict):
    """
    A helper class to deal with firmata command bytes. Set it up with a
    dictionary of commandnames and there bytes. Then add handlers for certain
    commands with ``add_handler``. Allows for accessing the commands as
    attributes.
    """
    _handlers = {}
    def __init__(self, bytes_dict):
        if not type(bytes_dict):
            bytes_dicts = dict(bytes_dict)
        self = bytes_dict
        
    def __getattr__(self, name):
        return self[name]
    
    def add_handler(self, command, handler):
        if not command in self:
            raise ValueError, "This command does not exist yet. Add it first with add_command"
        self._handlers[command] = handler

    def add_command(self, command, byte):
        self[command] = byte
    
    def get_handler(self, command):
        try:
            return self._handlers[command]
        except IndexError:
            raise NotImplementedError, "A handler for %s has not been defined yet." % chr(command)

class Iterator(threading.Thread):
    def __init__(self, arduino):
        super(Iterator, self).__init__()
        self.arduino = arduino
        
    def run(self):
        while 1:
            try:
                while self.arduino.iterate():
                    self.arduino.iterate()
                time.sleep(0.001)
            except (AttributeError, SerialException, OSError), e:
                # this way we can kill the thread by setting the arduino object
                # to None, or when the serial port is closed by arduino.exit()
                break
            except Exception, e:
                # catch 'error: Bad file descriptor'
                # iterate may be called while the serial port is being closed,
                # causing an "error: (9, 'Bad file descriptor')"
                if getattr(e, 'errno', None) == 9:
                    break
                try:
                    if e[0] == 9:
                        break
                except (TypeError, IndexError):
                    pass
                raise

def break_to_bytes(value):
    """
    Breaks a value into values of less than 255 that form value when multiplied.
    (Or almost do so with primes)
    Returns a tuple
    
    >>> break_to_bytes(200)
    (200,)
    >>> break_to_bytes(800)
    (200, 4)
    >>> break_to_bytes(802)
    (2, 2, 200)
    """
    if value < 256:
        return (value,)
    c = 256
    least = (0, 255)
    for i in range(254):
        c -= 1
        rest = value % c
        if rest == 0 and value / c < 256:
            return (c, value / c)
        elif rest == 0 and value / c > 255:
            parts = list(break_to_bytes(value / c))
            parts.insert(0, c)
            return tuple(parts)
        else:
            if rest < least[1]:
                least = (c, rest)
    return (c, value / c)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
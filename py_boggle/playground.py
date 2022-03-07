from collections.abc import Iterator

class MyIter(Iterator):
  def __init__(self) -> None:
      
    pass

  def __iter__(self) -> typing.Iterator[str]:
    pass
  # raise NotImplementedError("method __iter__") # TODO: implement your code here

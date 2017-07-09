# CBA
This is my implementation of algorithm CBA (Classification Based on Associations). It's my final project of data mining course, taught by [Prof. Chen Lin]. It's written by Python 3.6. You can read the paper [Integrating Classification and Association Rule Mining] by Bing Liu et al. for details.

## What's in datasets?
The datasets are chosen from [UCI Machine Learning Repository] and processed simply. We download 30 datasets including some classical datasets like [iris].

Each dataset has 2 files: 

- `*.data` contains many instances. Each line represents a sample. The attributes of the instance are divided by comma mark (,) without the space ( ). The last attribute is the class label, both number or literal string are vaild.
- `*.names` contains two lines. The first line is title line, describing the name of each attribute. The last word must be **`class`**, representing the class label. The second line is the type of each attribute, only **`numerical`** and **`categorical`** are acceptable. The last word must be **`label`**. The words in both lines are all divided by comma mark (,) without space ( ).

Moreover, the names of two files must be the **same**.

You can open `iris.data` and `iris.names` under `datasets` directory to understand the rules above.

## How to run it?
The entry of code is in the file `validation.py`. You can modify the `test_data_path` and `test_scheme_path` at the end of file. All datasets can be found in `datasets` directory. I provide 4 running modes: CBA-CB M1/M2 with/without pruning. Choose one mode you want to run, keep that line available and comment out the other three lines. 

For example, if you want to take [iris] dataset as test data, just let `test_data_path = datasets/iris.data` and `test_scheme_path = datasets/iris.names`. And if you want to test CBA-CB M1 without pruning, you can prefix the last three lines with hash mark (\#), like

```python
# just choose one mode to experiment by removing one line comment and running
cross_validate_m1_without_prune(test_data_path, test_scheme_path)
# cross_validate_m1_with_prune(test_data_path, test_scheme_path)
# cross_validate_m2_without_prune(test_data_path, test_scheme_path)
# cross_validate_m1_with_prune(test_data_path, test_scheme_path)
```
Then you can run the program.

## Acknowledgment
Dasong Chen and Lujing Xiao assisted me to complete this project. Thanks for their effort.

## Reference
[1] Liu, Bing, W. Hsu, and Y. Ma. "Integrating Classification and Association Rule Mining." Proc of Kdd (1998):80--86.

[Integrating Classification and Association Rule Mining]: http://kckckc.myweb.hinet.net/paper/Integrating_Classification_and_Association_Rule_Mining.pdf
[Prof. Chen Lin]: http://www.cs.xmu.edu.cn/cs/node/155
[iris]: http://archive.ics.uci.edu/ml/datasets/Iris
[UCI Machine Learning Repository]: http://archive.ics.uci.edu/ml/index.php
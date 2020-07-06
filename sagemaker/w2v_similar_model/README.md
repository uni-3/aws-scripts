gensim word2vec model for train or prediction on sagemaker.

### train

you should put train file like...

```
word1 word2 word3
word1 word4
...
```

### prediction

return similar words from `topn(default=5)` 

ex)

```
{
  'word': word,
  'similarity': 1.00
}
```

#### refer 

- sample code using scikit learn

https://github.com/awslabs/amazon-sagemaker-examples/tree/master/advanced_functionality/scikit_bring_your_own

- sagemaker sdk

https://sagemaker.readthedocs.io/en/stable/index.html
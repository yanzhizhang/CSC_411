'''
Question 2.2 Skeleton Code

Here you should implement and evaluate the Conditional Gaussian classifier.
'''

import data
import numpy as np
# Import pyplot - plt.imshow is useful!
import matplotlib.pyplot as plt

def compute_mean_mles(train_data, train_labels):
    '''
    Compute the mean estimate for each digit class

    Should return a numpy array of size (10,64)
    The ith row will correspond to the mean estimate for digit class i
    '''
    means = np.zeros((10, 64))
    # Compute means
    counter = [0]*10
    for index, label in enumerate(train_labels):
        ith = int(label)
        data = train_data[index]
        means[ith] += data
        counter[ith] += 1
    true_means = []
    for index, i in enumerate(means):
        i = i/counter[index]
        true_means.append(i)
    return np.asarray(true_means)

def compute_sigma_mles(train_data, train_labels):
    '''
    Compute the covariance estimate for each digit class

    Should return a three dimensional numpy array of shape (10, 64, 64)
    consisting of a covariance matrix for each digit class
    '''
    covariances = [[]]*10
    true_covariances = [[]]*10
    means = compute_mean_mles(train_data, train_labels)
    # Compute covariances
    for index, label in enumerate(train_labels):
        ith = int(label)
        data = train_data[index]
        covariances[ith] = covariances[ith] + list([data])

    covariances = np.asarray(covariances)
    for index in range(len(covariances)):
        class_i_mean = np.tile(means[index],(covariances[index].shape[0],1))
        true_covariances[index] = np.matmul( np.subtract(covariances[index], class_i_mean).T, np.subtract(covariances[index], class_i_mean))

    true_covariances = np.array(true_covariances)

    #to ensure numerical stability
    for i in true_covariances:
        for j in range(i.shape[0]):
            i[j][j] += 0.01

    return np.asarray(true_covariances)

def plot_cov_diagonal(covariances):
    # Plot the diagonal of each covariance matrix side by side
    diags = []
    for i in range(10):
        cov_diag = np.log(np.diag(covariances[i]))
        diags.append(cov_diag.reshape((8, 8)))
    diags = np.asarray(diags)
    all_concat = np.concatenate(diags, 1)
    plt.imshow(all_concat, cmap='gray')
    plt.show()

def generative_likelihood(digits, means, covariances):
    '''
    Compute the generative log-likelihood:
        log p(x|y,mu,Sigma)

    Should return an n x 10 numpy array
    '''
    gen = []
    for i in range(digits.shape[0]):
        likelihood = []
        for j in range(10):
            denominator = ((2 * np.pi) ** (- digits.shape[1] / 2)) * ((np.linalg.det(covariances[j])) ** (-0.5))
            numerator = np.exp((-0.5) * (digits[i] - means[j]).transpose().dot(np.linalg.inv(covariances[j]))
                            .dot((digits[i] - means[j])))
            likelihood.append(np.log(denominator) + np.log(numerator))
        gen.append(np.array(likelihood))
    return np.array(gen)

def conditional_likelihood(digits, means, covariances):
    '''
    Compute the conditional likelihood:

        log p(y|x, mu, Sigma)

    This should be a numpy array of shape (n, 10)
    Where n is the number of datapoints and 10 corresponds to each digit class
    '''
    gen = generative_likelihood(digits, means, covariances)
    x = []
    for i in range(digits.shape[0]):
        evidence = []
        for j in range(10):
            denominator = ((2 * np.pi) ** (- digits.shape[1] / 2)) * ((np.linalg.det(covariances[j])) ** (-0.5))
            numerator = (digits[i] - means[j]).transpose().dot(np.linalg.inv(covariances[j])).dot((digits[i] - means[j]))
            evidence.append(np.log(denominator) + np.exp(np.log(numerator)))
        x.append(np.array(evidence))
    return gen + np.log(1/10) - np.array(x)


def avg_conditional_likelihood(digits, labels, means, covariances):
    '''
    Compute the average conditional likelihood over the true class labels

        AVG( log p(y_i|x_i, mu, Sigma) )

    i.e. the average log likelihood that the model assigns to the correct class label
    '''
    # Compute as described above and return
    cond_likelihood = conditional_likelihood(digits, means, covariances)
    true_likeihood = []
    labels.astype(int)

    for index in range(labels.shape[0]):
        temp = int(labels[index])
        true_likeihood.append(cond_likelihood[index][temp])
    true_likeihood = np.asarray(true_likeihood)
    return np.mean(true_likeihood, axis=0)

def classify_data(digits, means, covariances):
    '''
    Classify new points by taking the most likely posterior class
    '''
    cond_likelihood = conditional_likelihood(digits, means, covariances)
    # Compute and return the most likely class
    return np.argmax(cond_likelihood, axis=1)

def main():
    train_data, train_labels, test_data, test_labels = data.load_all_data('data')

    # Fit the model
    means = compute_mean_mles(train_data, train_labels)
    covariances = compute_sigma_mles(train_data, train_labels)
    plot_cov_diagonal(covariances)

    # Evaluation

    print("Average conditional likelihood over the true training class labels is %f" %avg_conditional_likelihood(train_data, train_labels, means, covariances))
    print("Average conditional likelihood over the true testing class labels is %f" %avg_conditional_likelihood(test_data, test_labels, means, covariances))

    classify = classify_data(test_data, means, covariances)
    correct = 0
    for i in range(classify.shape[0]):
        if classify[i] == test_labels[i]:
            correct += 1
    accuracy = correct / classify.shape[0]
    print("Conditional Gaussian classifier on testing set has an accuracy of %f." %accuracy)

    classify = classify_data(train_data, means, covariances)
    correct = 0
    for i in range(classify.shape[0]):
        if classify[i] == train_labels[i]:
            correct += 1
    accuracy = correct / classify.shape[0]
    print("Conditional Gaussian classifier on training set has an accuracy of %f." %accuracy)


if __name__ == '__main__':
    main()

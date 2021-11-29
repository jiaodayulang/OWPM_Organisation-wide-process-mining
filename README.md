# OWPM_Organisation-wide-process-mining
## Introduction
The complexity of organisational processes is a key challenge for any organisation, especially for organisations with a large-scale and huge variety of processes. Comparatively, conducting process identification can help organisations to focus on processes having substantial problems at an early stage and deliver maximum value in BPM projects. This research presents a novel method for automated process identification using a data-drive approach and statistical process performance measurements. This method consists of two main steps: process enumeration and process selection. A systematic approach for process enumeration is proposed to automatically enumerate all possible processes from the event data scattered in various information systems. Then, a method for process selection is applied to evaluate the enumerated processes and assess them based on statistical process performance measurements. Our research shows the validity and efficiency of our method for process identification through experimental analysis using real-world data (MIMIC-III Clinical Database) and in-depth interviews with experts.
<p align="center"><img src="https://github.com/jiaodayulang/OWPM_Orgnisation-wide-process-mining/blob/main/Image Folder/BPM lifecycle.png" width="300"></p>
<p align="center"><em>Figure: BPM lifecycle</em></p>
<p align="center"><img src="https://github.com/jiaodayulang/OWPM_Orgnisation-wide-process-mining/blob/main/Image Folder/process_identification_1.png" width="600"></p>
<p align="center"><em>Figure: Conceptual Framework for Process Identification</em></p>

## Method for automated process identification
### Stage 1: Process enumeration
<p align="center"><img src="https://github.com/jiaodayulang/OWPM_Orgnisation-wide-process-mining/blob/main/Image Folder/Conceptual Case ID Identification matching example.png" width="500"></p>

#### Prototype development
<p align="center"><img src="https://github.com/jiaodayulang/OWPM_Orgnisation-wide-process-mining/blob/main/Image Folder/PrototypeDev.png" width="400"></p>

### Stage 2: Process performance evaluation
#### Method 1: Coefficient of Simple Linear Regression
A time series regression with a time trend as the independent variable

𝑊_𝑡=𝛽_0+𝛽_1 𝑡+𝜀_𝑡![image](https://user-images.githubusercontent.com/37859948/143956829-035185fe-d94b-43b5-9e28-f76230032841.png)


Where 𝛽_0 and 𝛽_1 (the intercept and slope, respectively) using the observed data 𝑊_1,𝑊_2, … 𝑊_𝑛, and a serial of 𝜀_𝑡′𝑠 are random errors are not observed

The slope of the trend line: 
𝛽_1=  (𝑛∑_(𝑡=1)^𝑛▒〖𝑡𝑊_𝑡 〗  −∑_(𝑡=1)^𝑛▒〖𝑡 ∑_(𝑡=1)^𝑛▒𝑊_𝑡 〗)/(𝑛∑_(𝑡=1)^𝑛▒𝑡^2  〖−(∑_(𝑡=1)^𝑛▒𝑡)〗^2 )![image](https://user-images.githubusercontent.com/37859948/143957506-f4b5a6e2-81e4-4c10-945d-54a5e5f429a8.png)

\beta_1=\frac{n \sum_{t=1}^{n} tW_t- \sum_{t=1}^{n}t \sum_{t=1}^{n}W_t}{n\sum_{t=1}^{n}t^2-(\sum_{t=1}^{n}t)^2}  

F=P (1+(i/n)^n

<p align="center"><img src="https://github.com/jiaodayulang/OWPM_Orgnisation-wide-process-mining/blob/main/Image Folder/disctributionChanges.png" width="400"></p>
<p align="center"><img src="https://github.com/jiaodayulang/OWPM_Orgnisation-wide-process-mining/blob/main/Image Folder/PerformanceIndexCal.png" width="500"></p>

#### Method 2: Control chart


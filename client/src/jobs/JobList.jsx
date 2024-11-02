// ~/legal-doc-system/client/src/jobs/JobList.jsx
import React from 'react';
import JobCard from './JobCard';

const JobList = ({ jobs }) => {
    return (
        <div>
            {jobs.map((job) => (
                <JobCard key={job.id} job={job} />
            ))}
        </div>
    );
};

export default JobList;

/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/workers/reportWorker.js
 *
 * Report Worker
 * -------------
 * Example worker that processes queued report generation tasks.
 */

const { startTask, completeTask, failTask } = require('../services/taskService');
const Task = require('../models/taskModel');
const Report = require('../models/reportModel');

exports.processReports = async () => {
    const tasks = await Task.find({ type: 'report.generate', status: 'queued' }).sort({ priority: 1, queuedAt: 1 }).limit(10);
    for (const t of tasks) {
        try {
            await startTask(t._id);
            // Example processing (replace with real rendering)
            const reportId = t.payload?.reportId;
            const report = await Report.findById(reportId).lean();
            // ... generate PDF, store file, update report ...
            await completeTask(t._id, { reportId, status: 'pdf_generated' });
        } catch (err) {
            await failTask(t._id, err.message);
        }
    }
};
